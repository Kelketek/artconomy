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
            <v-col cols="12" sm="6" v-if="(is(NEW) || is(PAYMENT_PENDING) || is(WAITING)) && isSeller">
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
                  <ac-confirmation :action="statusEndpoint('accept')" v-if="is(NEW) || is(WAITING)">
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
                  <v-col class="text-center payment-section" v-if="is(PAYMENT_PENDING) && isBuyer && !deliverable.x.escrow_disabled" cols="12" >
                    <v-col v-if="is(PAYMENT_PENDING) && isStaff" class="text-center" cols="12">
                      <v-btn @click="showManualTransaction = true">Transaction Input</v-btn>
                      <ac-form-dialog v-model="showManualTransaction" @submit.prevent="paymentForm.submitThen(updateDeliverable)" v-bind="paymentForm.bind" title="Enter transaction ID">
                        <v-row>
                          <v-col cols="6">
                            <ac-bound-field :field="paymentForm.fields.cash" label="Cash transaction" hint="Tick this box if the customer has handed you cash." field-type="ac-checkbox" />
                          </v-col>
                          <v-col cols="6">
                            <ac-bound-field :disabled="paymentForm.fields.cash.value" :field="paymentForm.fields.remote_id" label="Transaction ID" hint="Enter the transaction ID given to you by the Authorize.net app." />
                          </v-col>
                        </v-row>
                      </ac-form-dialog>
                    </v-col>
                    <v-btn color="green" @click="showPayment = true" class="payment-button">Send Payment</v-btn>
                    <ac-form-dialog v-model="showPayment" @submit.prevent="paymentForm.submitThen(updateDeliverable)" :large="true" v-bind="paymentForm.bind">
                      <v-row>
                        <v-col class="text-center" cols="12" >Total Charge: <strong>${{totalCharge.toFixed(2)}}</strong></v-col>
                        <v-col cols="12">
                          <ac-load-section :controller="order">
                            <template v-slot:default>
                              <ac-card-manager
                                ref="cardManager"
                                :payment="true"
                                :username="buyer.username"
                                :cc-form="paymentForm"
                                :field-mode="true"
                                v-model="paymentForm.fields.card_id.model"
                              />
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
          </v-row>
        </template>
      </ac-load-section>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {ListController} from '@/store/lists/controller'
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
@Component({
  components: {
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
  },
})
export default class DeliverablePayment extends mixins(DeliverableMixin, Formatting) {
  public showPayment = false
  public showManualTransaction = false

  @Watch('showManualTransaction')
  public clearManualTransactionSettings() {
    this.paymentForm.fields.cash.update(false)
    this.paymentForm.fields.remote_id.update('')
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

  public get bareLines() {
    return this.lineItems.list.map((x) => (x.x as LineItem))
  }

  public get totalCharge() {
    return this.priceData.total
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
    if (this.tip) {
      this.tip.patchers.amount.model = tip.toFixed(2)
    } else {
      this.tipForm.fields.amount.update(tip.toFixed(2))
      this.tipForm.submitThen(this.lineItems.uniquePush)
    }
  }

  public get tip() {
    return this.lineItems && this.lineItems.list.filter((x) => x.x && x.x.type === LineTypes.TIP)[0]
  }
}
</script>
