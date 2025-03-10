<template>
  <ac-load-section
    v-if="seller"
    :controller="deliverable"
  >
    <template #default>
      <ac-load-section :controller="lineItems">
        <template #default>
          <v-row v-if="deliverable.x && order.x">
            <v-col
              cols="12"
              md="6"
            >
              <v-col
                cols="12"
                class="text-center text-md-left"
              >
                <div>
                  <span>Placed on: {{ formatDateTime(deliverable.x.created_on) }}</span><br>
                  <span v-if="revisionCount">
                    <strong>{{ revisionCount }}</strong> revision<span v-if="revisionCount > 1">s</span> included.
                  </span><br>
                  <span v-if="deliveryDate">Estimated completion: <strong>{{
                    formatDateTerse(deliveryDate.toISOString())
                  }}</strong></span><br>
                  <span v-if="isSeller">Slots taken: <strong>{{ taskWeight }}</strong></span>
                </div>
              </v-col>
              <v-col
                v-if="is(DeliverableStatus.NEW) && isBuyer"
                cols="12"
              >
                <v-alert type="info">
                  This order is pending approval. The artist may adjust pricing depending on the piece's requirements.
                  You can send payment once the order is approved.
                </v-alert>
              </v-col>
              <v-col
                v-if="isSeller && editable"
                cols="12"
              >
                <v-row no-gutters>
                  <v-col cols="12">
                    <ac-patch-field
                      :patcher="deliverable.patchers.adjustment"
                      field-type="ac-price-field"
                      label="Surcharges/Discounts (USD)"
                    />
                  </v-col>
                  <v-col cols="12">
                    <ac-patch-field
                      :patcher="deliverable.patchers.adjustment_expected_turnaround"
                      label="Additional Days Required"
                    />
                  </v-col>
                  <v-col cols="12">
                    <ac-patch-field
                      :patcher="deliverable.patchers.adjustment_revisions"
                      label="Additional Revisions Offered"
                    />
                  </v-col>
                  <v-col cols="12">
                    <ac-patch-field
                      :patcher="deliverable.patchers.adjustment_task_weight"
                      label="Additional slots consumed"
                    />
                  </v-col>
                </v-row>
              </v-col>
              <v-col
                v-if="isSeller && editable"
                cols="12"
              >
                <ac-patch-field
                  :patcher="deliverable.patchers.escrow_enabled"
                  field-type="v-switch"
                  label="Shield Protection"
                  :persistent-hint="true"
                  hint="If turned off, disables shield protection. In this case, you
                  will have to handle payment using a third party service, or collecting it in person."
                  color="primary"
                />
              </v-col>
              <v-col
                v-if="isSeller && editable && seller.paypal_configured"
                cols="12"
              >
                <ac-patch-field
                  :patcher="deliverable.patchers.paypal"
                  field-type="v-switch"
                  label="Paypal Invoicing"
                  :persistent-hint="true"
                  :disabled="deliverable.patchers.escrow_enabled.model"
                  hint="Create an invoice in PayPal for this order."
                  color="primary"
                />
              </v-col>
              <v-col
                v-if="isSeller && editable"
                cols="12"
              >
                <ac-patch-field
                  :patcher="deliverable.patchers.cascade_fees"
                  field-type="v-switch"
                  label="Absorb fees"
                  :persistent-hint="true"
                  hint="If turned on, the price you set is the price your commissioner will see, and you
                            will pay all fees from that price. If turned off, the price you set is the amount you
                            take home, and the total the customer pays includes the fees."
                  color="primary"
                />
              </v-col>
            </v-col>
            <v-col
              cols="12"
              md="6"
            >
              <v-col cols="12">
                <v-card>
                  <v-card-text>
                    <ac-price-preview
                      :price="deliverable.x.price"
                      :line-items="lineItems"
                      :username="order.x.seller.username"
                      :is-seller="isSeller"
                      :editable="editable && (isSeller || isArbitrator)"
                      :edit-base="!product"
                      :disabled="stateChange.sending"
                      :escrow="deliverable.x.escrow_enabled"
                    />
                    <v-row v-if="deliverable.x.paid_on">
                      <v-col class="text-center">
                        <v-icon
                          left
                          color="green"
                          :icon="mdiCheckCircle"
                        />
                        Paid on {{ formatDate(deliverable.x.paid_on) }}
                      </v-col>
                    </v-row>
                    <v-row v-if="isBuyer && is(DeliverableStatus.NEW)">
                      <v-col class="text-center">
                        <p>
                          <strong>Note:</strong> The artist may adjust the above price based on the requirements you
                          have given before accepting it.
                        </p>
                      </v-col>
                    </v-row>
                    <ac-escrow-label
                      :escrow="escrow"
                      name="order"
                    />
                    <v-col
                      v-if="paypalUrl"
                      class="text-center"
                      cols="12"
                    >
                      <v-btn
                        color="primary"
                        target="_blank"
                        rel="noopener"
                        variant="elevated"
                        :href="paypalUrl"
                      >
                        <span v-if="is(DeliverableStatus.PAYMENT_PENDING) && isBuyer">Pay with PayPal</span>
                        <span v-else>View Invoice on PayPal</span>
                      </v-btn>
                    </v-col>
                    <v-col
                      v-if="isSeller && editable"
                      class="text-center"
                      cols="12"
                    >
                      <ac-confirmation
                        v-if="is(DeliverableStatus.NEW, DeliverableStatus.WAITING) && isSeller"
                        :action="statusEndpoint('accept')"
                      >
                        <template #default="{on}">
                          <v-btn
                            color="green"
                            class="accept-order"
                            variant="elevated"
                            :disabled="stateChange.sending"
                            v-on="on"
                          >
                            Accept
                            Order
                          </v-btn>
                        </template>
                        <template #confirmation-text>
                          <v-col>
                            I understand the commissioner's requirements, and I agree to be bound by the
                            <router-link :to="{name: 'CommissionAgreement'}">
                              Commission agreement
                            </router-link>
                            .
                          </v-col>
                        </template>
                        <template #title>
                          <span>Accept Order</span>
                        </template>
                        <template #confirm-text>
                          <span>I agree</span>
                        </template>
                      </ac-confirmation>
                      <v-btn
                        v-else-if="is(DeliverableStatus.NEW, DeliverableStatus.WAITING) && powers.table_seller"
                        color="green"
                        class="accept-order"
                        :disabled="stateChange.sending"
                        variant="flat"
                        @click="statusEndpoint('accept')()"
                      >
                        Accept Order
                      </v-btn>
                    </v-col>
                    <v-col
                      v-if="(isSeller || isArbitrator) && (is(DeliverableStatus.QUEUED, DeliverableStatus.IN_PROGRESS, DeliverableStatus.REVIEW, DeliverableStatus.DISPUTED)) && !paypalUrl"
                      class="text-center"
                      cols="12"
                    >
                      <ac-confirmation :action="statusEndpoint('refund')">
                        <template #default="{on}">
                          <v-btn
                            variant="flat"
                            color="red"
                            v-on="on"
                          >
                            <span v-if="escrow">Refund</span>
                            <span v-else>Mark Refunded</span>
                          </v-btn>
                        </template>
                      </ac-confirmation>
                    </v-col>
                    <v-col
                      v-if="is(DeliverableStatus.PAYMENT_PENDING) && (isBuyer || powers.table_seller) && deliverable.x.escrow_enabled"
                      class="text-center payment-section"
                      cols="12"
                    >
                      <v-btn
                        color="green"
                        variant="flat"
                        class="payment-button"
                        @click="viewSettings.patchers.showPayment.model = true"
                      >
                        Send Payment
                      </v-btn>
                      <ac-form-dialog
                        v-model="viewSettings.patchers.showPayment.model"
                        :large="true"
                        v-bind="paymentForm.bind"
                        :show-submit="showSubmit"
                        @submit.prevent="paymentSubmit"
                      >
                        <v-row>
                          <v-col
                            class="text-center"
                            cols="12"
                          >
                            Total Charge:
                            <strong>${{ totalCharge }}</strong>
                          </v-col>
                          <v-col cols="12">
                            <ac-load-section :controller="deliverable">
                              <template #default>
                                <v-tabs
                                  v-if="powers.table_seller"
                                  v-model="cardTabs"
                                  fixed-tabs
                                  class="mb-2"
                                >
                                  <v-tab>Manual Entry</v-tab>
                                  <v-tab>Terminal</v-tab>
                                  <v-tab>Cash</v-tab>
                                </v-tabs>
                                <v-window v-model="cardTabs">
                                  <v-window-item>
                                    <ac-card-manager
                                      ref="cardManager"
                                      v-model="paymentForm.fields.card_id.model"
                                      :payment="true"
                                      :username="buyer!.username"
                                      :cc-form="paymentForm"
                                      :field-mode="true"
                                      :client-secret="(clientSecret.x && clientSecret.x.secret) || ''"
                                      @payment-sent="hideForm"
                                    />
                                  </v-window-item>
                                  <v-window-item>
                                    <ac-paginated :list="readers">
                                      <template #default>
                                        <ac-form-container v-bind="readerForm.bind">
                                          <v-row no-gutters>
                                            <v-col
                                              cols="12"
                                              md="6"
                                              offset-md="3"
                                            >
                                              <v-card elevation="10">
                                                <v-card-text>
                                                  <v-row>
                                                    <v-col
                                                      v-for="reader in readers.list"
                                                      :key="reader.x!.id"
                                                      cols="12"
                                                    >
                                                      <v-radio-group v-model="readerForm.fields.reader.model">
                                                        <ac-bound-field
                                                          field-type="v-radio"
                                                          :field="readerForm.fields.reader"
                                                          :value="reader.x!.id"
                                                          :label="reader.x!.name"
                                                        />
                                                      </v-radio-group>
                                                    </v-col>
                                                    <v-col
                                                      cols="12"
                                                      @click="readerForm.submit()"
                                                    >
                                                      <v-btn
                                                        color="green"
                                                        block
                                                        variant="flat"
                                                      >
                                                        Activate Reader
                                                      </v-btn>
                                                    </v-col>
                                                  </v-row>
                                                </v-card-text>
                                              </v-card>
                                            </v-col>
                                          </v-row>
                                        </ac-form-container>
                                      </template>
                                    </ac-paginated>
                                  </v-window-item>
                                  <v-window-item>
                                    <v-row>
                                      <v-col
                                        cols="12"
                                        md="6"
                                        offset-md="3"
                                        class="pa-5"
                                      >
                                        <v-btn
                                          color="primary"
                                          block
                                          class="mark-paid-cash"
                                          variant="flat"
                                          @click="paymentForm.submitThen(updateDeliverable)"
                                        >
                                          Mark Paid by Cash
                                        </v-btn>
                                      </v-col>
                                    </v-row>
                                  </v-window-item>
                                </v-window>
                              </template>
                            </ac-load-section>
                          </v-col>
                          <v-col
                            class="text-center"
                            cols="12"
                          >
                            <p>
                              Use of Artconomy is subject to the
                              <router-link :to="{name: 'TermsOfService'}">
                                Terms of Service
                              </router-link>
                              .<br>
                              This order is subject to the
                              <router-link :to="{name: 'CommissionAgreement'}">
                                Commission Agreement
                              </router-link>
                              .<br>
                              Artconomy is based in the United States of America.
                            </p>
                          </v-col>
                        </v-row>
                      </ac-form-dialog>
                    </v-col>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-col>
            <v-col cols="12">
              <v-card>
                <v-card-text>
                  <v-list-subheader v-if="commissionInfo">
                    Commission Info
                  </v-list-subheader>
                  <ac-rendered
                    :value="commissionInfo"
                    :truncate="200"
                  />
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </ac-load-section>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import {DeliverableProps, useDeliverable} from '@/components/views/order/mixins/DeliverableMixin.ts'
import {getTotals} from '@/lib/lineItemFunctions.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcRendered from '@/components/wrappers/AcRendered.ts'
import {useStripeHost} from '@/components/views/order/mixins/StripeHostMixin.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {mdiCheckCircle} from '@mdi/js'
import {computed, ref, Ref, watch} from 'vue'
import {useSingle} from '@/store/singles/hooks.ts'
import {DeliverableStatus} from '@/types/enums/DeliverableStatus.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {formatDate, formatDateTime, formatDateTerse} from '@/lib/otherFormatters.ts'
import type {ClientSecret, LineAccumulator, LineItem} from '@/types/main'

const props = defineProps<DeliverableProps>()
const {
  powers,
  viewerHandler,
} = useViewer()

const canUpdate = ref(false)
const {
  buyer,
  seller,
  deliveryDate,
  paypalUrl,
  paymentForm,
  prefix,
  url,
  deliverable,
  is,
  isBuyer,
  isSeller,
  isArbitrator,
  lineItems,
  viewSettings,
  sellerHandler,
  expectedTurnaround,
  outputs,
  buyerSubmission,
  sellerSubmission,
  escrow,
  revisions,
  characters,
  statusEndpoint,
  stateChange,
  editable,
  revisionCount,
  taskWeight,
  updateDeliverable,
  product,
  order,
} = useDeliverable(props)
const cardTabs = ref(0)

const showSubmit = computed(() => {
  return cardTabs.value !== 1
})

const oldTotal: Ref<null | string> = ref(null)

const clientSecret = useSingle<ClientSecret>(
    `${prefix.value}__clientSecret`, {
      endpoint: `${url.value}payment-intent/`,
    },
)

const cardManager = ref<typeof AcCardManager | null>(null)

const invoiceUrl = computed(() => {
  return `/api/sales/invoice/${deliverable.x?.invoice}/`
})

const readerFormUrl = computed(() => {
  return `${invoiceUrl.value}stripe-process-present-card/`
})

const {
  readers,
  updateIntent,
  readerForm,
  debouncedUpdateIntent,
} = useStripeHost({
  clientSecret,
  readerFormUrl,
  paymentForm,
  canUpdate,
})

watch(() => deliverable.x?.invoice, (val: string | null | undefined) => {
  if (!val) {
    return
  }
  clientSecret.endpoint = `${invoiceUrl.value}payment-intent/`
  canUpdate.value = true
  updateIntent()
}, {immediate: true})

const bareLines = computed(() => {
  return lineItems.list.map((x) => (x.x as LineItem))
})

const priceData = computed((): LineAccumulator => {
  /* istanbul ignore if */
  return getTotals(bareLines.value)
})

const totalCharge = computed(() => {
  return priceData.value.total
})

watch(totalCharge, (value: string) => {
  paymentForm.fields.amount.update(value)
})

const hideForm = () => {
  viewSettings.patchers.showPayment.model = false
  paymentForm.sending = false
}

const paymentSubmit = () => {
  cardManager.value?.stripeSubmit()
}

const commissionInfo = computed(() => {
  if (!sellerHandler) {
    return ''
  }
  if (is(DeliverableStatus.NEW, DeliverableStatus.PAYMENT_PENDING)) {
    if (!sellerHandler.artistProfile.x) {
      return ''
    }
    return sellerHandler.artistProfile.x.commission_info
  }
  /* istanbul ignore if */
  if (!deliverable.x) {
    return ''
  }
  return deliverable.x.commission_info
})

watch(totalCharge, (val: string | undefined) => {
  if (val === undefined || !isBuyer.value) {
    return
  }
  if (oldTotal.value && !(oldTotal.value === val)) {
    updateIntent()
  }
  oldTotal.value = val
})

watch(powers, (newVal) => {
  if (newVal.table_seller) {
    return
  }
  cardTabs.value = 0
  paymentForm.fields.use_reader.update(false)
  paymentForm.fields.cash.update(false)
  updateIntent()
})

watch(isBuyer, (val: boolean | null) => {
  if (!val) {
    return
  }
  updateIntent()
}, {immediate: false})

watch(() => readers.ready, (val: boolean) => {
  if (val && powers.value.table_seller && readers.list.length) {
    cardTabs.value = 1
  }
})

watch(cardTabs, (tabValue: number) => {
  if (tabValue === 2) {
    paymentForm.fields.cash.update(true)
  } else {
    paymentForm.fields.cash.update(false)
  }
  if (tabValue === 1) {
    paymentForm.fields.use_reader.update(true)
    if (readers.list.length && !readerForm.fields.reader.value) {
      readerForm.fields.reader.update(readers.list[0].x!.id)
    }
  } else {
    paymentForm.fields.use_reader.update(false)
  }
  updateIntent()
})

// Several tests depend on setting these to make sure content loads. They're a holdover from Vue 2 object inheritance,
// and they need rewriting.
defineExpose({
  expectedTurnaround,
  revisions,
  characters,
  viewerHandler,
  debouncedUpdateIntent,
  buyerSubmission,
  sellerSubmission,
  deliveryDate,
  outputs,
})
</script>
