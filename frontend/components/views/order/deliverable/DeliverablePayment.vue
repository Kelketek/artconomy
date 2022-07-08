<template>
  <ac-load-section :controller="deliverable" v-if="seller">
    <template v-slot:default>
      <ac-load-section :controller="lineItems">
        <template v-slot:default>
          <v-row v-if="is(NEW) && isBuyer">
            <v-col>
              <v-alert type="info">
                  This order is pending approval. The artist may adjust pricing depending on the piece's requirements.
                  You can send payment once the order is approved.
              </v-alert>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6" class="text-center text-md-left">
              Placed on: {{formatDateTime(deliverable.x.created_on)}}<br />
              <span v-if="revisionCount">
                    <strong>{{revisionCount}}</strong> revision<span v-if="revisionCount > 1">s</span> included.
              </span>
            </v-col>
            <v-col cols="6" class="text-center text-md-left">
              <div>
                <span>Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong></span><br />
                <span v-if="isSeller">Slots taken: <strong>{{taskWeight}}</strong></span>
              </div>
            </v-col>
            <v-col cols="12" sm="6" v-if="(is(NEW) || is(PAYMENT_PENDING) || is(WAITING)) && (isSeller || isStaff)">
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
                <v-col class="text-center" cols="12" >
                  <ac-confirmation :action="statusEndpoint('accept')" v-if="(is(NEW) || is(WAITING)) && isSeller">
                    <template v-slot:default="{on}">
                      <v-btn v-on="on" color="green" class="accept-order">Accept Order</v-btn>
                    </template>
                    <v-col slot="confirmation-text">
                      I understand the commissioner's requirements, and I agree to be bound by the
                      <router-link :to="{name: 'CommissionAgreement'}">Commission agreement</router-link>.
                    </v-col>
                    <span slot="title">Accept Order</span>
                    <span slot="confirm-text">I agree</span>
                  </ac-confirmation>
                  <v-btn color="green" class="accept-order" @click="statusEndpoint('accept')()" v-else-if="(is(NEW) || is(WAITING)) && isStaff">
                    Accept Order
                  </v-btn>
                </v-col>
                <v-col cols="12">
                  <ac-escrow-label :escrow="escrow" name="order" />
                </v-col>
              </v-row>
            </v-col>
            <v-col v-else cols="12" sm="6">
              <ac-escrow-label :escrow="escrow" name="order" />
            </v-col>
            <v-col cols="12" sm="6">
              <v-card>
                <v-card-text>
                  <ac-price-preview
                    :price="deliverable.x.price"
                    :line-items="lineItems"
                    :username="order.x.seller.username"
                    :is-seller="isSeller"
                    :editable="(is(NEW) || is(PAYMENT_PENDING) || is(WAITING)) && (isSeller || isArbitrator)"
                    :editBase="!product"
                    :escrow="!deliverable.x.escrow_disabled"
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
                  <ac-escrow-label :escrow="escrow" name="order" v-if="$vuetify.breakpoint.smAndDown" />
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
                  <v-col class="text-center payment-section" v-if="is(PAYMENT_PENDING) && (isBuyer || isStaff) && !deliverable.x.escrow_disabled" cols="12" >
                    <v-btn color="green" @click="showPayment = true" class="payment-button">Send Payment</v-btn>
                    <ac-form-dialog
                        v-model="showPayment" @submit.prevent="paymentSubmit"
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
                                        <v-btn color="primary" block @click="paymentForm.submitThen(updateDeliverable)">
                                          Mark Paid by Cash
                                        </v-btn>
                                      </v-col>
                                    </v-row>
                                  </v-tab-item>
                                </v-tabs-items>
                              </template>
                            </ac-load-section>
                          </v-col>
                          <v-col cols="12" v-if="seller.landscape && !deliverable.x.escrow_disabled" class="text-xs-center">
                            <v-card elevation="5">
                              <v-card-title>Add a tip?</v-card-title>
                              <v-card-text>
                                <ac-form-container v-bind="tipForm.bind">
                                  <ac-form @submit.prevent="tipForm.submitThen(lineItems.uniquePush)">
                                    <v-row>
                                      <v-col cols="12">
                                        <strong>Tips are not required, as artists set their own prices,</strong> but they are always appreciated. Your tip is protected
                                        by Artconomy Shield, along with the rest of your order.
                                      </v-col>
                                      <v-col cols="4" sm="2" offset-sm="3" class="text-center">
                                        <v-btn small color="secondary" class="preset10" fab @click="setTip(.1)"><strong>10%</strong></v-btn>
                                      </v-col>
                                      <v-col cols="4" sm="2" class="text-center">
                                        <v-btn small color="secondary" class="preset15" fab @click="setTip(.15)"><strong>15%</strong></v-btn>
                                      </v-col>
                                      <v-col cols="4" sm="2" class="text-center">
                                        <v-btn small color="secondary" class="preset20" fab @click="setTip(.2)"><strong>20%</strong></v-btn>
                                      </v-col>
                                      <v-col cols="12" v-if="tip">
                                        <ac-patch-field
                                          :patcher="tip.patchers.amount"
                                          field-type="ac-price-field"
                                          label="Tip"
                                        />
                                      </v-col>
                                      <v-col cols="12" v-else class="text-center">
                                        <v-btn color="secondary" @click="setTip(0)">Custom Tip</v-btn>
                                      </v-col>
                                    </v-row>
                                  </ac-form>
                                </ac-form-container>
                              </v-card-text>
                            </v-card>
                          </v-col>
                          <v-col class="text-center" cols="12" v-if="tip">
                            <ac-price-preview
                              :price="deliverable.x.price"
                              :line-items="lineItems"
                              :username="order.x.seller.username"
                              :is-seller="isSeller"
                              :escrow="!order.x.escrow_disabled"
                            />
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
import Big from 'big.js'
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
  public showPayment = false
  public clientSecret = null as unknown as SingleController<ClientSecret>
  public PROCESSORS = PROCESSORS
  public socketState = null as unknown as SingleController<SocketState>
  public oldTotal: null | Big = null
  // Setting this false to avoid calling for the secret until we have the invoice ID.
  public canUpdateStorage = false
  public cardTabs = 0

  @Watch('cardTabs')
  public clearManualTransactionSettings(tabValue: number) {
    if (tabValue === 2) {
      this.paymentForm.fields.cash.update(true)
    } else {
      this.paymentForm.fields.cash.update(false)
    }
    if ((tabValue === 1) && this.readers.list.length) {
      if (!this.readerForm.fields.reader.value) {
        this.readerForm.fields.reader.update(this.readers.list[0].x!.id)
      }
      this.paymentForm.fields.use_reader.update(true)
    } else {
      this.paymentForm.fields.use_reader.update(false)
    }
    this.updateIntent()
  }

  @Watch('proxyTotalCharge')
  public updateAmount(newValue: Big, oldValue: Big|undefined) {
    this.paymentForm.fields.amount.update(this.totalCharge)
    /* istanbul ignore if */
    if (oldValue === undefined) {
      return
    }
    if (newValue.eq(oldValue)) {
      // Vue can't quite tell when these are equal otherwise.
      return
    }
    if (newValue.eq(Big('0')) || oldValue.eq(Big('0'))) {
      // Refresh the line items, since if it's newly 0, or no longer 0, upstream may have changed.
      this.lineItems.get()
    }
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
    this.showPayment = false
    this.paymentForm.sending = false
  }

  public get invoiceUrl() {
    return `/api/sales/v1/invoices/${this.deliverable.x?.invoice}/`
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
  public triggerFetchReaders(isStaff: boolean, oldVal: boolean) {
    if (!isStaff) {
      this.cardTabs = 0
      this.paymentForm.fields.use_terminal.update(false)
      this.paymentForm.fields.cash.update(false)
      this.updateIntent()
      return
    }
    if (!oldVal && !(this.readers.ready || this.readers.fetching)) {
      if (!this.stripe()) {
        setTimeout(() => {
          this.triggerFetchReaders(isStaff, oldVal)
        }, 500)
        return
      }
      this.fetchReaders()
    }
  }

  public get priceData(): LineAccumulator {
    /* istanbul ignore if */
    if (!this.lineItems) {
      return {total: Big(0), map: new Map(), discount: Big(0)}
    }
    return getTotals(this.bareLines)
  }

  public get proxyTotalCharge(): Big|undefined {
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
  public forceRefetch(val: undefined | Big) {
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

  public setTip(multiplier: number) {
    const subTotal = totalForTypes(getTotals(this.sansOutsiders), [
      LineTypes.BASE_PRICE, LineTypes.ADD_ON, LineTypes.BONUS, LineTypes.SHIELD,
    ])
    const tip = quantize(subTotal.times(multiplier))
    let promise: Promise<LineItem | void>
    if (this.tip) {
      this.tipForm.sending = true
      const amount = parseFloat(tip.toFixed(2))
      promise = this.tip.patch({amount}).then(() => {
        this.tip.patchers.amount.model = amount
      })
    } else {
      this.tipForm.fields.amount.update(tip.toFixed(2))
      promise = this.tipForm.submitThen(this.lineItems.uniquePush)
    }
    promise.then(() => {
      this.tipForm.sending = false
    })
  }

  public get tip() {
    return this.lineItems && this.lineItems.list.filter((x) => x.x && x.x.type === LineTypes.TIP)[0]
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
