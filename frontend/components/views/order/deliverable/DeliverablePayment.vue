<template>
  <ac-load-section :controller="deliverable" v-if="seller">
    <template v-slot:default>
      <ac-load-section :controller="lineItems">
        <template v-slot:default>
          <v-row>
            <v-col cols="12" md="6">
              <v-col cols="12" class="text-center text-md-left">
                <div>
                  <span>Placed on: {{formatDateTime(deliverable.x.created_on)}}</span><br />
                  <span v-if="revisionCount">
                    <strong>{{revisionCount}}</strong> revision<span v-if="revisionCount > 1">s</span> included.
                </span><br />
                  <span>Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong></span><br />
                  <span v-if="isSeller">Slots taken: <strong>{{taskWeight}}</strong></span>
                </div>
              </v-col>
              <v-col cols="12" v-if="is(NEW) && isBuyer">
                <v-alert type="info">
                  This order is pending approval. The artist may adjust pricing depending on the piece's requirements.
                  You can send payment once the order is approved.
                </v-alert>
              </v-col>
              <v-col cols="12" v-if="isSeller && editable">
                <v-row no-gutters  >
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
              <v-col cols="12" v-if="isSeller && editable">
                <ac-patch-field
                    :patcher="deliverable.patchers.escrow_enabled" field-type="v-switch" label="Shield Protection" :persistent-hint="true"
                    hint="If turned off, disables shield protection. In this case, you
                  will have to handle payment using a third party service, or collecting it in person."
                />
              </v-col>
              <v-col cols="12" v-if="isSeller && editable">
                <ac-patch-field
                    :patcher="deliverable.patchers.cascade_fees" field-type="v-switch" label="Absorb fees" :persistent-hint="true"
                    hint="If turned on, the price you set is the price your commissioner will see, and you
                            will pay all fees from that price. If turned off, the price you set is the amount you
                            take home, and the total the customer pays includes the fees."
                />
              </v-col>
            </v-col>
            <v-col cols="12" md="6">
              <v-col cols="12">
                <v-card>
                  <v-card-text>
                    <ac-price-preview
                        :price="deliverable.x.price"
                        :line-items="lineItems"
                        :username="order.x.seller.username"
                        :is-seller="isSeller"
                        :editable="editable && (isSeller || isArbitrator)"
                        :editBase="!product"
                        :escrow="deliverable.x.escrow_enabled"
                    />
                    <v-row v-if="deliverable.x.paid_on">
                      <v-col class="text-center">
                        <v-icon left color="green">check_circle</v-icon> Paid on {{formatDate(deliverable.x.paid_on)}}
                      </v-col>
                    </v-row>
                    <v-row v-if="isBuyer && is(NEW)">
                      <v-col class="text-center">
                        <p><strong>Note:</strong> The artist may adjust the above price based on the requirements you have given before accepting it.</p>
                      </v-col>
                    </v-row>
                    <ac-escrow-label :escrow="escrow" name="order" />
                    <v-col class="text-center" cols="12" v-if="isSeller && editable">
                      <ac-confirmation :action="statusEndpoint('accept')" v-if="(is(NEW) || is(WAITING)) && isSeller">
                        <template v-slot:default="{on}">
                          <v-btn v-on="on" color="green" class="accept-order">Accept Order</v-btn>
                        </template>
                        <template v-slot:confirmation-text>
                          <v-col>
                            I understand the commissioner's requirements, and I agree to be bound by the
                            <router-link :to="{name: 'CommissionAgreement'}">Commission agreement</router-link>.
                          </v-col>
                        </template>
                        <span slot="title">Accept Order</span>
                        <span slot="confirm-text">I agree</span>
                      </ac-confirmation>
                      <v-btn color="green" class="accept-order" @click="statusEndpoint('accept')()" v-else-if="(is(NEW) || is(WAITING)) && isStaff">
                        Accept Order
                      </v-btn>
                    </v-col>
                    <v-col class="text-center" v-if="(isSeller || isArbitrator) && (is(QUEUED) || is(IN_PROGRESS) || is(REVIEW) || is(DISPUTED))" cols="12" >
                      <ac-confirmation :action="statusEndpoint('refund')">
                        <template v-slot:default="{on}">
                          <v-btn v-on="on">
                            <span v-if="escrow">Refund</span>
                            <span v-else>Mark Refunded</span>
                          </v-btn>
                        </template>
                      </ac-confirmation>
                    </v-col>
                    <v-col class="text-center payment-section" v-if="is(PAYMENT_PENDING) && (isBuyer || isStaff) && deliverable.x.escrow_enabled" cols="12" >
                      <v-btn color="green" @click="viewSettings.patchers.showPayment.model = true" class="payment-button">Send Payment</v-btn>
                      <ac-form-dialog
                          v-model="viewSettings.patchers.showPayment.model" @submit.prevent="paymentSubmit"
                          :large="true" v-bind="paymentForm.bind"
                          :show-submit="showSubmit"
                      >
                        <v-row>
                          <v-col class="text-center" cols="12" >Total Charge: <strong>${{totalCharge.toFixed(2)}}</strong></v-col>
                          <v-col cols="12">
                            <ac-load-section :controller="deliverable">
                              <template v-slot:default>
                                <v-tabs fixed-tabs class="mb-2" v-model="cardTabs" v-if="isStaff">
                                  <v-tab>Manual Entry</v-tab>
                                  <v-tab>Terminal</v-tab>
                                  <v-tab>Cash</v-tab>
                                </v-tabs>
                                <v-tabs-items v-model="cardTabs">
                                  <v-tab-item>
                                    <ac-card-manager
                                        ref="cardManager"
                                        :payment="true"
                                        :username="buyer.username"
                                        :processor="deliverable.x.processor"
                                        :cc-form="paymentForm"
                                        :field-mode="true"
                                        :client-secret="(clientSecret.x && clientSecret.x.secret) || ''"
                                        v-model="paymentForm.fields.card_id.model"
                                        @paymentSent="hideForm"
                                    />
                                  </v-tab-item>
                                  <v-tab-item>
                                    <ac-paginated :list="readers">
                                      <template v-slot:default>
                                        <ac-form-container v-bind="readerForm.bind">
                                          <v-row no-gutters>
                                            <v-col cols="12" md="6" offset-md="3">
                                              <v-card elevation="10">
                                                <v-card-text>
                                                  <v-row>
                                                    <v-col v-for="reader in readers.list" :key="reader.x.id" cols="12">
                                                      <v-radio-group v-model="readerForm.fields.reader.model">
                                                        <ac-bound-field
                                                            field-type="v-radio"
                                                            :field="readerForm.fields.reader"
                                                            :value="reader.x.id"
                                                            :label="reader.x.name"
                                                        />
                                                      </v-radio-group>
                                                    </v-col>
                                                    <v-col cols="12" @click="readerForm.submit()">
                                                      <v-btn color="green" block>Activate Reader</v-btn>
                                                    </v-col>
                                                  </v-row>
                                                </v-card-text>
                                              </v-card>
                                            </v-col>
                                          </v-row>
                                        </ac-form-container>
                                      </template>
                                    </ac-paginated>
                                  </v-tab-item>
                                  <v-tab-item>
                                    <v-row>
                                      <v-col cols="12" md="6" offset-md="3" class="pa-5">
                                        <v-btn color="primary" block class="mark-paid-cash" @click="paymentForm.submitThen(updateDeliverable)">
                                          Mark Paid by Cash
                                        </v-btn>
                                      </v-col>
                                    </v-row>
                                  </v-tab-item>
                                </v-tabs-items>
                              </template>
                            </ac-load-section>
                          </v-col>
                          <v-col class="text-center" cols="12" >
                            <p>Use of Artconomy is subject to the
                              <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>.<br />
                              This order is subject to the <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement</router-link>.<br />
                              Artconomy is based in the United States of America.</p>
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
                  <v-subheader v-if="commissionInfo">Commission Info</v-subheader>
                  <ac-rendered :value="commissionInfo" :truncate="200" />
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </ac-load-section>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import LineItem from '@/types/LineItem'
import DeliverableMixin from '@/components/views/order/mixins/DeliverableMixin'
import {Watch} from 'vue-property-decorator'
import {Decimal} from 'decimal.js'
import LineAccumulator from '@/types/LineAccumulator'
import {getTotals, quantize, totalForTypes} from '@/lib/lineItemFunctions'
import {LineTypes} from '@/types/LineTypes'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Formatting from '@/mixins/formatting'
import AcBoundField from '@/components/fields/AcBoundField'
import AcRendered from '@/components/wrappers/AcRendered'
import {SingleController} from '@/store/singles/controller'
import ClientSecret from '@/types/ClientSecret'
import {PROCESSORS} from '@/types/PROCESSORS'
import AcStripeCharge from '@/components/AcStripeCharge.vue'
import {SocketState} from '@/types/SocketState'
import StripeHostMixin from '@/components/views/order/mixins/StripeHostMixin'
import StripeMixin from '../mixins/StripeMixin'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'

@Component({
  components: {
    AcPaginated,
    AcStripeCharge,
    AcBoundField,
    AcPatchField,
    AcForm,
    AcFormContainer,
    AcCardManager,
    AcFormDialog,
    AcConfirmation,
    AcEscrowLabel,
    AcPricePreview,
    AcLoadSection,
    AcRendered,
  },
})
export default class DeliverablePayment extends mixins(DeliverableMixin, Formatting, StripeHostMixin, StripeMixin) {
  public clientSecret = null as unknown as SingleController<ClientSecret>
  public PROCESSORS = PROCESSORS
  public socketState = null as unknown as SingleController<SocketState>
  public oldTotal: null | Decimal = null
  // Setting this false to avoid calling for the secret until we have the invoice ID.
  public canUpdateStorage = false
  public cardTabs = 0
  public destroyed = false

  @Watch('cardTabs')
  public clearManualTransactionSettings(tabValue: number) {
    if (tabValue === 2) {
      this.paymentForm.fields.cash.update(true)
    } else {
      this.paymentForm.fields.cash.update(false)
    }
    if (tabValue === 1) {
      this.paymentForm.fields.use_reader.update(true)
      if (this.readers.list.length && !this.readerForm.fields.reader.value) {
        this.readerForm.fields.reader.update(this.readers.list[0].x!.id)
      }
    } else {
      this.paymentForm.fields.use_reader.update(false)
    }
    this.updateIntent()
  }

  @Watch('proxyTotalCharge')
  public updateAmount(newValue: Decimal, oldValue: Decimal|undefined) {
    this.paymentForm.fields.amount.update(this.totalCharge)
  }

  public get canUpdate() {
    return this.canUpdateStorage
  }

  public get showSubmit() {
    return this.cardTabs !== 1
  }

  @Watch('deliverable.x.invoice')
  public updateSecretEndpoint(val: string | undefined) {
    if (!val) {
      return
    }
    this.clientSecret.endpoint = `${this.invoiceUrl}payment-intent/`
    this.readerForm.endpoint = this.readerFormUrl
    this.canUpdateStorage = true
    this.updateIntent()
  }

  public hideForm() {
    this.viewSettings.patchers.showPayment.model = false
    this.paymentForm.sending = false
  }

  public get invoiceUrl() {
    return `/api/sales/v1/invoice/${this.deliverable.x?.invoice}/`
  }

  public get readerFormUrl() {
    return `${this.invoiceUrl}stripe-process-present-card/`
  }

  @Watch('readers.ready')
  public setTab(val: boolean) {
    if (val && this.isStaff && this.readers.list.length) {
      this.cardTabs = 1
    }
  }

  @Watch('isBuyer', {immediate: false})
  public fetchSecret(isBuyer: boolean) {
    if (!isBuyer) {
      return
    }
    this.updateIntent()
  }

  @Watch('isStaff')
  public setNonStaffTab(isStaff: boolean, oldVal: boolean) {
    if (!isStaff) {
      this.cardTabs = 0
      this.paymentForm.fields.use_reader.update(false)
      this.paymentForm.fields.cash.update(false)
      this.updateIntent()
    }
  }

  public get priceData(): LineAccumulator {
    /* istanbul ignore if */
    if (!this.lineItems) {
      return {total: new Decimal(0), subtotals: new Map(), discount: new Decimal(0)}
    }
    return getTotals(this.bareLines)
  }

  public get proxyTotalCharge(): Decimal|undefined {
    // We return zero on the normal priceData if lineItems is null, but this causes the
    // watcher to trigger when it shouldn't.
    if (this.lineItems === null) {
      return undefined
    }
    return this.totalCharge
  }

  public paymentSubmit() {
    const cardManager = this.$refs.cardManager as any
    cardManager.stripeSubmit()
  }

  public get commissionInfo() {
    if (!this.sellerHandler) {
      return ''
    }
    if (this.is(this.NEW) || this.is(this.PAYMENT_PENDING)) {
      if (!this.sellerHandler.artistProfile.x) {
        return ''
      }
      return this.sellerHandler.artistProfile.x.commission_info
    }
    /* istanbul ignore if */
    if (!this.deliverable.x) {
      return ''
    }
    return this.deliverable.x.commission_info
  }

  public get bareLines() {
    return this.lineItems.list.map((x) => (x.x as LineItem))
  }

  public get totalCharge() {
    return this.priceData.total
  }

  @Watch('totalCharge')
  public forceRefetch(val: undefined | Decimal) {
    if (val === undefined || !this.isBuyer) {
      return
    }
    if (this.oldTotal && !this.oldTotal.eq(val)) {
      this.updateIntent()
    }
    this.oldTotal = val
  }

  public get sansOutsiders() {
    return this.bareLines.filter((x) => [
      LineTypes.BASE_PRICE, LineTypes.ADD_ON, LineTypes.BONUS, LineTypes.SHIELD,
    ].includes(x.type))
  }

  public created() {
    this.socketState = this.$getSingle('socketState')
    this.clientSecret = this.$getSingle(
        `${this.prefix}__clientSecret`, {
          endpoint: `${this.url}payment-intent/`,
        })
  }
}
</script>
