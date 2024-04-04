<template>
  <ac-load-section :controller="invoice">
    <template v-slot:default>
      <ac-load-section :controller="lineItems" v-if="invoice.x">
        <template v-slot:default>
          <v-card elevation="10" v-if="(invoice.x.status === DRAFT) && isBuyer">
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
          <v-card v-else-if="(invoice.x.status === VOID) && isBuyer">
            <v-card-text class="text-center">
              <ac-form-container v-bind="tipForm.bind">
                <v-row>
                  <v-col cols="12"><strong>You declined to tip.</strong></v-col>
                  <v-col cols="12">
                    <v-btn color="primary" @click="reissueTipInvoice" variant="flat">I changed my mind</v-btn>
                  </v-col>
                </v-row>
              </ac-form-container>
            </v-card-text>
          </v-card>
          <v-card v-else-if="invoice.x.status === PAID">
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

<script lang="ts">
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import {getTotals, quantize, reckonLines, totalForTypes} from '@/lib/lineItemFunctions.ts'
import {LineTypes} from '@/types/LineTypes.ts'
import LineItem from '@/types/LineItem.ts'
import {ListController} from '@/store/lists/controller.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Invoice from '@/types/Invoice.ts'
import {SingleController} from '@/store/singles/controller.ts'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import {artCall, baseCardSchema} from '@/lib/lib.ts'
import StripeHostMixin from '../mixins/StripeHostMixin.ts'
import {InvoiceStatus} from '@/types/InvoiceStatus.ts'
import Subjective from '@/mixins/subjective.ts'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import Deliverable from '@/types/Deliverable.ts'
import {mdiCheckCircle} from '@mdi/js'

@Component({
  components: {
    AcFormDialog,
    AcCardManager,
    AcPatchField,
    AcFormContainer,
    AcForm,
    AcLoadSection,
    AcPricePreview,
  },
})
class AcTippingPrompt extends mixins(Subjective, StripeHostMixin) {
  @Prop({required: true})
  public invoiceId!: string

  @Prop({required: true})
  public sourceLines!: ListController<LineItem>

  @Prop({required: true})
  public deliverable!: SingleController<Deliverable>

  @Prop({required: true})
  public isBuyer!: boolean

  public mdiCheckCircle = mdiCheckCircle
  public invoice = null as unknown as SingleController<Invoice>

  public lineItems = null as unknown as ListController<LineItem>
  public tipForm = null as unknown as FormController
  public stateChange = null as unknown as FormController
  public paymentForm = null as unknown as FormController

  public DRAFT = InvoiceStatus.DRAFT
  public OPEN = InvoiceStatus.OPEN
  public VOID = InvoiceStatus.VOID
  public PAID = InvoiceStatus.PAID

  public get sansOutsiders() {
    return this.bareLines.filter((x) => [
      LineTypes.BASE_PRICE, LineTypes.ADD_ON, LineTypes.BONUS, LineTypes.SHIELD,
      LineTypes.PROCESSING,
    ].includes(x.type))
  }

  @Watch('invoice.x.status')
  public updateForStatus(status: InvoiceStatus) {
    if (status === InvoiceStatus.OPEN) {
      this.updateIntent()
    }
  }

  public get showSendTip() {
    return !!(this.invoice.x && this.invoice.x.status === InvoiceStatus.OPEN)
  }

  public set showSendTip(val: boolean) {
    if (val) {
      // Nonsense-- we're only using this for cancelling.
      return
    }
    this.paymentForm.sending = true
    this.statusEndpoint('void')().finally(() => {
      this.paymentForm.sending = false
    })
  }

  public get bareLines() {
    return this.sourceLines.list.map((x) => (x.x as LineItem))
  }

  public get deliverableUrl() {
    return `/api/sales/order/${this.deliverable.x!.order.id}/deliverables/${this.deliverable.x!.id}/`
  }

  public paymentSubmit() {
    const cardManager = this.$refs.cardManager as any
    cardManager.stripeSubmit()
  }

  public reissueTipInvoice() {
    this.tipForm.sending = true
    // Will update invoice by updating the deliverable over websocket, reloading this component with the new invoice ID.
    artCall({
      url: `${this.deliverableUrl}issue-tip-invoice/`,
      method: 'post',
    }).then((invoice: Invoice) => {
      this.deliverable.updateX({invoice: invoice.id})
    }).finally(() => {
      this.tipForm.sending = false
    })
  }

  public setTip(multiplier: number) {
    const subTotal = totalForTypes(getTotals(this.sansOutsiders), [
      LineTypes.BASE_PRICE, LineTypes.ADD_ON, LineTypes.BONUS, LineTypes.SHIELD,
    ])
    const tip = quantize(subTotal.times(multiplier))
    const amount = parseFloat(tip.toFixed(2))
    this.tip.patchers.amount.model = amount
  }

  public get tip() {
    return this.lineItems && this.lineItems.list.filter((x) => x.x && x.x.type === LineTypes.TIP)[0]
  }

  public get total() {
    return reckonLines(this.lineItems.list.map((controller) => controller.x!))
  }

  public get url() {
    return `/api/sales/invoice/${this.invoiceId}/`
  }

  public get readerFormUrl() {
    return `${this.url}stripe-process-present-card/`
  }

  public statusEndpoint(append: string) {
    return () => {
      this.stateChange.endpoint = `${this.url}${append}/`
      return this.stateChange.submitThen(this.invoice.setX)
    }
  }

  public created() {
    const schema = baseCardSchema(`${this.url}pay/`)
    schema.fields = {
      ...schema.fields,
      card_id: {value: null},
      service: {value: null},
      amount: {value: 0},
      remote_id: {value: ''},
      cash: {value: false},
    }
    this.clientSecret = this.$getSingle(
        `${this.invoiceId}__clientSecret`, {
          endpoint: `${this.url}payment-intent/`,
        })
    this.paymentForm = this.$getForm(`${this.invoiceId}__payment`, schema)
    this.invoice = this.$getSingle(
        `${this.invoiceId}`,
        {
          endpoint: this.url,
          socketSettings: {
            appLabel: 'sales',
            modelName: 'Invoice',
            serializer: 'InvoiceSerializer',
          },
        },
    )
    this.invoice.get()
    this.lineItems = this.$getList(`${this.invoiceId}__lines`, {
      endpoint: `${this.url}line-items/`,
      paginated: false,
      persistent: true,
      socketSettings: {
        appLabel: 'sales',
        modelName: 'LineItem',
        serializer: 'LineItemSerializer',
        list: {
          appLabel: 'sales',
          modelName: 'Invoice',
          pk: `${this.invoiceId}`,
          listName: 'line_items',
        },
      },
    })
    this.lineItems.firstRun()
    // Used as wrapper for state change events.
    this.stateChange = this.$getForm(
        `${this.invoiceId}__stateChange`, {
          endpoint: this.url,
          fields: {},
        },
    )
  }
}

export default toNative(AcTippingPrompt)
</script>
