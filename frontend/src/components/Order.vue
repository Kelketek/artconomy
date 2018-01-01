<template>
  <div>
    <div v-if="order" class="container">
      <div class="row shadowed">
        <div class="col-lg-4 col-sm-12 col-md-6 text-section text-center">
          <ac-asset :asset="order.product" thumb-name="preview" img-class="bound-image"></ac-asset>
        </div>
        <div class="col-md-6 col-sm-12 text-section pt-3">
          <h1 v-html="md.renderInline(order.product.name)"></h1>
          <h2>Order #{{order.id}}</h2>
          <div v-html="md.render(order.product.description)"></div>
          <div>
            <h4>Details:</h4>
            <div v-html="md.render(order.details)"></div>
          </div>
        </div>
        <div class="col-sm-12 col-lg-2 text-section text-center pt-3">
          <div class="text-center">
            <h3>Ordered By</h3>
            <ac-avatar :user="order.buyer"></ac-avatar>
          </div>
        </div>
        <div class="col-sm-12 text-section mb-2">
          <h2>Characters</h2>
        </div>
        <div class="col-sm-12">
          <ac-character-preview
              v-for="char in order.characters"
              v-bind:character="char"
              v-bind:expanded="true"
              v-bind:key="char.id"
          ></ac-character-preview>
        </div>
        <div class="col-lg-3 col-md-6 col-sm-12 text-section text-center pt-2">
          <h3>Seller:</h3>
          <ac-avatar :user="order.seller"></ac-avatar>
        </div>
        <div class="col-lg-6 col-md-6 col-sm-12 text-section text-center pt-2">
          <div class="pricing-container">
            <p v-if="order.status < 2">Price may be adjusted by the seller before finalization.</p>
            <span v-html="md.renderInline(order.product.name)"></span>: ${{order.price}}<br />
            <span v-if="adjustmentModel.adjustment < 0">Discount: </span>
            <span v-else-if="adjustmentModel.adjustment > 0">Custom requirements: </span>
            <span v-if="parseFloat(adjustmentModel.adjustment) !== 0">${{parseFloat(adjustmentModel.adjustment).toFixed(2)}}</span>
            <hr />
            <strong>Total: ${{price}}</strong>
            <div v-if="seller && sellerData.user.fee !== null">
              Artconomy service fee: -${{ fee }} <br />
              <strong>Your payout: ${{ payout }}</strong>
            </div>
        </div>
          <div class="pricing-container mt-2" v-if="seller && (newOrder || paymentPending) && (sellerData.user.fee !== null)">
            <ac-form-container
                ref="adjustmentForm"
                :schema="adjustmentSchema"
                :model="adjustmentModel"
                :url="`${url}adjust/`"
                method="PATCH"
                :reset-after="false">
            </ac-form-container>
            <div class="text-center">
              <b-button type="submit" variant="primary" @click.prevent="$refs.adjustmentForm.submit">Adjust price</b-button><i v-if="$refs.adjustmentForm && $refs.adjustmentForm.saved" class="fa fa-check" style="color: green"></i>
            </div>
            <p class="mt-2">
              <strong>Note:</strong> Only one adjustment may be used. Therefore, please include all
              discounts and increases in the adjustment price. Be sure to comment so that the commissioner
              will see your reasoning. Do not approve a request until you have added your adjustment, as that
              will finalize the price.
            </p>
          </div>
        </div>
        <div class="col-lg-3 col-sm-12 text-section pt-2">
          <div v-if="buyer && newOrder">
            <p>
              <strong>The artist has been notified of your order, and will respond soon!</strong>
            </p>
            <p>We will notify you once the artist has completed their review.</p>
          </div>
          <div v-if="seller && (newOrder)">
            <p><strong>Make any Price adjustments here, and then accept or reject the order.</strong></p>
            <p>Be sure to comment on the order about your price adjustments so the buyer will know the reasoning behind them.</p>
          </div>
          <div v-if="seller && paymentPending">
            <p><strong>We've notified the commissioner of your acceptance!</strong></p>
            <p>We will notify you once they have paid for the commission. You are advised not to begin work until payment has been received. If needed, you may adjust the pricing until the comissioner pays.</p>
          </div>
          <div v-if="buyer && paymentPending">
            <p><strong>The artist has accepted your commission! Please pay below.</strong></p>
            <p>Review the price and pay below. Once your payment has been received, your commission will be placed in the artist's queue.</p>
          </div>
          <div class="text-center mb-3" v-if="newOrder || paymentPending">
            <ac-action :url="`${this.url}cancel/`" variant="danger" :success="populateOrder">Cancel</ac-action>
            <ac-action v-if="newOrder" :confirm="true" :url="`${this.url}accept/`" variant="success" :success="populateOrder">
              Approve order
              <div class="text-left" slot="confirmation-text">
                <p>
                  Are you sure you understand the commissioner's requirements? By accepting this order, you are confirming you
                  understand and agree to the <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement.</router-link>
                </p>
              </div>
            </ac-action>
          </div>
          <div v-if="cancelled">
            <strong>This order has been cancelled.</strong>
          </div>
        </div>
      </div>
      <div class="mb-5">
        <ac-comment-section :commenturl="commenturl" :nesting="false"></ac-comment-section>
      </div>
    </div>
    <div class="row" v-else>
      <div class="text-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    </div>
  </div>
</template>

<script>
  import AcCharacterPreview from './ac-character-preview'
  import AcAction from './ac-action'
  import AcCommentSection from './ac-comment-section'
  import AcAvatar from './ac-avatar'
  import AcPatchfield from './ac-patchfield'
  import AcAsset from './ac-asset'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import { artCall, md } from '../lib'
  import AcFormContainer from './ac-form-container'

  export default {
    name: 'Order',
    props: ['orderID'],
    components: {
      AcFormContainer,
      AcCharacterPreview,
      AcAvatar,
      AcPatchfield,
      AcAsset,
      AcCommentSection,
      AcAction
    },
    mixins: [Viewer, Perms],
    methods: {
      populateOrder (response) {
        let oldAdjustment = this.order && this.order.adjustment
        this.order = response
        if (oldAdjustment === null) {
          this.adjustmentModel.adjustment = response.adjustment
        }
        this.$root.setUser(response.seller.username, this.sellerData, this.$error)
      }
    },
    computed: {
      newOrder () {
        return this.order.status === 1
      },
      paymentPending () {
        return this.order.status === 2
      },
      queued () {
        return this.order.status === 3
      },
      cancelled () {
        return this.order.status === 6
      },
      price () {
        return (parseFloat(this.order.price) + parseFloat(this.adjustmentModel.adjustment)).toFixed(2)
      },
      buyer () {
        return ((this.viewer.username === this.order.buyer.username) || this.viewer.is_staff)
      },
      seller () {
        return ((this.viewer.username === this.order.seller.username) || this.viewer.is_staff)
      },
      fee () {
        return (this.price * (this.sellerData.user.fee).toFixed(2)).toFixed(2)
      },
      payout () {
        return (this.price - this.fee).toFixed(2)
      }
    },
    data () {
      return {
        order: null,
        commenturl: `/api/sales/v1/order/${this.orderID}/comments/`,
        url: `/api/sales/v1/order/${this.orderID}/`,
        md: md,
        sellerData: {user: {fee: null}},
        adjustmentModel: {
          adjustment: 0.00
        },
        adjustmentSchema: {
          fields: [{
            type: 'input',
            inputType: 'number',
            step: '.01',
            model: 'adjustment',
            label: 'Adjustment (USD)',
            featured: true
          }]
        }
      }
    },
    created () {
      artCall(this.url, 'GET', undefined, this.populateOrder, this.$error)
    }
  }
</script>

<style scoped>
   .v-align-middle {
     vertical-align: middle;
   }
  .pricing-container {
    display: inline-block;
    text-align: left;
  }
  .max-width {
    width: 100%;
  }
</style>