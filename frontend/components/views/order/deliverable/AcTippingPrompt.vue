<template>
  <ac-load-section :controller="invoice">
    <template v-slot:default>
      <ac-load-section :controller="lineItems" v-if="invoice.x">
        <template v-slot:default>
          <v-card elevation="10" v-if="(invoice.x.status === InvoiceStatus.DRAFT) && isBuyer">
            <v-card-text>
              <v-row class="text-center">
                <v-col cols="12">
                  <div class="text-center title">Add a tip?</div>
                  <ac-form-container v-bind="paymentForm.bind">
                    <ac-form @submit.prevent="statusEndpoint('finalize')()">
                      <v-row>
                        <v-col cols="12">
                          <strong>Tips are not required, as artists set their own prices,</strong> but they are always
                          appreciated.
                        </v-col>
                        <v-col cols="4" sm="2" offset-sm="3" class="text-center">
                          <v-btn small color="secondary" class="preset10" icon @click="setTip(.1)"><strong>10%</strong>
                          </v-btn>
                        </v-col>
                        <v-col cols="4" sm="2" class="text-center">
                          <v-btn small color="secondary" class="preset15" icon @click="setTip(.15)"><strong>15%</strong>
                          </v-btn>
                        </v-col>
                        <v-col cols="4" sm="2" class="text-center">
                          <v-btn small color="secondary" class="preset20" icon @click="setTip(.2)"><strong>20%</strong>
                          </v-btn>
                        </v-col>
                        <v-col cols="12" v-if="tip">
                          <ac-patch-field
                              :patcher="tip.patchers.amount"
                              field-type="ac-price-field"
                              label="Tip"
                          />
                        </v-col>
                        <v-col cols="12" v-if="total">
                          <v-btn @click="statusEndpoint('finalize')()" color="primary" variant="flat">Send Tip</v-btn>
                        </v-col>
                      </v-row>
                    </ac-form>
                  </ac-form-container>
                </v-col>
                <v-col class="text-center" cols="12" v-if="tip">
                  <ac-price-preview :line-items="lineItems" :username="viewer!.username" :isSeller="false"
                                    :transfer="true" :hide-hourly-form="true"/>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          <ac-form-dialog
              v-else-if="showSendTip && isBuyer"
              v-model="showSendTip"
              :persistent="true"
              submit-text="Send Tip"
              cancel-text="Cancel Tip"
              v-bind="paymentForm.bind"
              :large="true"
              @submit.prevent="paymentSubmit"
          >
            <v-card-text>
              <v-row class="text-center">
                <v-col cols="12">
                  <ac-card-manager
                      ref="cardManager"
                      :payment="true"
                      :username="username"
                      :cc-form="paymentForm"
                      :field-mode="true"
                      :client-secret="(clientSecret.x && clientSecret.x.secret) || ''"
                      v-model="paymentForm.fields.card_id.model"
                  />
                </v-col>
                <v-col cols="12">
                  <ac-price-preview
                      :line-items="lineItems"
                      :username="viewer!.username"
                      :isSeller="false"
                      :transfer="true"
                      :hide-hourly-form="true"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </ac-form-dialog>
          <v-card v-else-if="(invoice.x.status === InvoiceStatus.VOID) && isBuyer">
            <v-card-text class="text-center">
              <ac-form-container v-bind="tipForm.bind">
                <v-row>
                  <v-col cols="12"><strong>You declined to tip.</strong></v-col>
                  <v-col cols="12">
                    <v-btn color="primary" @click="tipForm.submitThen(props.deliverable.updateX)" variant="flat">I changed my
                      mind
                    </v-btn>
                  </v-col>
                </v-row>
              </ac-form-container>
            </v-card-text>
          </v-card>
          <v-card v-else-if="invoice.x.status === InvoiceStatus.PAID">
            <v-col class="text-center">
              <v-icon left color="green" :icon="mdiCheckCircle"/>
              <span v-if="isBuyer">Tip Sent!</span>
              <span v-else>Tip Received!</span>
            </v-col>
            <v-col cols="12">
              <ac-price-preview
                  :line-items="lineItems"
                  :username="viewer!.username"
                  :isSeller="false"
                  :transfer="true"
                  :hide-hourly-form="true"
              />
            </v-col>
          </v-card>
        </template>
      </ac-load-section>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import {getTotals, reckonLines, totalForTypes} from '@/lib/lineItemFunctions.ts'
import {LineTypes} from '@/types/LineTypes.ts'
import LineItem from '@/types/LineItem.ts'
import {ListController} from '@/store/lists/controller.ts'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Invoice from '@/types/Invoice.ts'
import {SingleController} from '@/store/singles/controller.ts'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import {baseCardSchema} from '@/lib/lib.ts'
import {InvoiceStatus} from '@/types/InvoiceStatus.ts'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import Deliverable from '@/types/Deliverable.ts'
import {mdiCheckCircle} from '@mdi/js'
import {useSingle} from '@/store/singles/hooks.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {computed, ref, watch, Ref} from 'vue'
import {useStripeHost} from '@/components/views/order/mixins/StripeHostMixin.ts'
import ClientSecret from '@/types/ClientSecret.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {useList} from '@/store/lists/hooks.ts'
import SubjectiveProps from '@/types/SubjectiveProps.ts'

declare interface AcTippingPromptProps {
  invoiceId: string,
  sourceLines: ListController<LineItem>,
  deliverable: SingleController<Deliverable>,
  isBuyer: boolean|null,
}

const props = defineProps<SubjectiveProps & AcTippingPromptProps>()

const {viewer} = useViewer()

const url = computed(() => {
  return `/api/sales/invoice/${props.invoiceId}/`
})

const readerFormUrl = computed(() => {
  return `${url.value}stripe-process-present-card/`
})

const bareLines = computed(() => {
  return props.sourceLines.list.map((x) => (x.x as LineItem))
})

const deliverableUrl = computed(() => {
  return `/api/sales/order/${props.deliverable.x?.order.id}/deliverables/${props.deliverable.x?.id}/`
})

const schema = baseCardSchema(`${url.value}pay/`)
schema.fields = {
  ...schema.fields,
  card_id: {value: null},
  service: {value: null},
  amount: {value: 0},
  remote_id: {value: ''},
  cash: {value: false},
}
const clientSecret = useSingle<ClientSecret>(
    `${props.invoiceId}__clientSecret`, {
      endpoint: `${url.value}payment-intent/`,
    })
const paymentForm = useForm(`${props.invoiceId}__payment`, schema)
const invoice = useSingle<Invoice>(
    `${props.invoiceId}`,
    {
      endpoint: url.value,
      socketSettings: {
        appLabel: 'sales',
        modelName: 'Invoice',
        serializer: 'InvoiceSerializer',
      },
    },
)
invoice.get()
const lineItems = useList<LineItem>(`${props.invoiceId}__lines`, {
  endpoint: `${url.value}line-items/`,
  paginated: false,
  persistent: true,
  socketSettings: {
    appLabel: 'sales',
    modelName: 'LineItem',
    serializer: 'LineItemSerializer',
    list: {
      appLabel: 'sales',
      modelName: 'Invoice',
      pk: `${props.invoiceId}`,
      listName: 'line_items',
    },
  },
})
lineItems.firstRun()
// Used as wrapper for state change events.
const stateChange = useForm(
    `${props.invoiceId}__stateChange`, {
      endpoint: url.value,
      fields: {},
    },
)

const sansOutsiders = computed(() => {
  return bareLines.value.filter((x) => [
    LineTypes.BASE_PRICE, LineTypes.ADD_ON, LineTypes.BONUS, LineTypes.SHIELD,
    LineTypes.PROCESSING,
  ].includes(x.type))
})

const showSendTip = computed({
  get() {
    return !!(invoice.x && invoice.x.status === InvoiceStatus.OPEN)
  },
  set(val: boolean) {
    if (val) {
      // Nonsense-- we're only using this for cancelling.
      return
    }
    paymentForm.sending = true
    statusEndpoint('void')().finally(() => {
      paymentForm.sending = false
    })
  },
})

const tip = computed(() => {
  return lineItems.list.filter((x) => x.x && x.x.type === LineTypes.TIP)[0]
})

const total = computed(() => {
  return reckonLines(lineItems.list.map((controller) => controller.x!))
})

const tipForm = useForm('tipForm', {
  endpoint: `${deliverableUrl.value}issue-tip-invoice/`,
  fields: {},
})

const cardManager: Ref<null | typeof AcCardManager> = ref(null)

const paymentSubmit = () => {
  if (!cardManager.value) {
    return
  }
  cardManager.value.stripeSubmit()
}

const setTip = (multiplier: number) => {
  const subTotal = totalForTypes(getTotals(sansOutsiders.value), [
    LineTypes.BASE_PRICE, LineTypes.ADD_ON, LineTypes.BONUS, LineTypes.SHIELD,
  ])
  const tipAmount = parseFloat(subTotal) * multiplier
  tip.value.patchers.amount.model = tipAmount.toFixed(2)
}

const statusEndpoint = (append: string) => {
  return () => {
    stateChange.endpoint = `${url.value}${append}/`
    return stateChange.submitThen(invoice.setX)
  }
}

const canUpdate = computed(() => true)

const {updateIntent} = useStripeHost({
  clientSecret,
  readerFormUrl,
  canUpdate,
  paymentForm,
})

watch(() => invoice.x?.status, (status) => {
  if (status === InvoiceStatus.OPEN) {
    updateIntent()
  }
})
</script>
