<template>
  <div>
    <v-container v-if="order">
      <v-card>
        <v-layout row wrap>
          <v-flex xs12 md6 lg4 text-xs-center class="pt-2 pb-2 pl-2 pr-2">
            <ac-asset :asset="order.product" thumb-name="preview" img-class="bound-image" />
          </v-flex>
          <v-flex xs12 md6 class="pt-3 pl-2 pr-2">
            <h1 v-html="md.renderInline(order.product.name)"></h1>
            <h2>Order #{{order.id}}</h2>
            <div v-html="md.render(order.product.description)"></div>
            <div>
              <h4>Details:</h4>
              <div class="order-details" v-html="md.render(order.details)"></div>
            </div>
            <div v-if="order.private">
              <p><strong>PRIVATE ORDER</strong></p>
            </div>
          </v-flex>
          <v-flex xs12 lg2 text-xs-center class="pt-3">
            <div class="text-xs-center">
              <h3>Ordered By</h3>
              <ac-avatar :user="order.buyer" />
            </div>
            <div class="text-xs-center" v-if="orderClosed">
              <ac-action :url="url" :send="{subscribed: !order.subscribed}" method="PUT" :success="populateOrder">
                <v-icon v-if="order.subscribed">volume_up</v-icon><v-icon v-else>volume_off</v-icon>
              </ac-action>
            </div>
          </v-flex>
        </v-layout>
      </v-card>
    </v-container>
    <v-container v-if="order" grid-list-md>
      <v-layout row wrap>
        <v-flex xs12 class="mb-2">
          <h2>Characters</h2>
        </v-flex>
        <ac-character-preview
            v-for="char in order.characters"
            v-bind:character="char"
            v-bind:expanded="true"
            v-bind:key="char.id"
            xs12 md4 lg3
        />
      </v-layout>
    </v-container>
    <v-container v-if="order">
      <v-card>
        <v-layout row wrap>
          <v-flex xs12 md6 lg2 text-xs-center class="pt-2">
            <h3>Seller:</h3>
            <ac-avatar :user="order.seller" />
          </v-flex>
          <v-flex xs12 md6 text-xs-center class="pt-2" v-if="paymentDetail">
            <div class="pricing-container">
              <p v-if="order.status < 2">Price may be adjusted by the seller before finalization.</p>
              <span v-html="md.renderInline(order.product.name)"></span>: ${{order.price}}<br />
              <span v-if="adjustmentModel.adjustment < 0">Discount: </span>
              <span v-else-if="adjustmentModel.adjustment > 0">Custom requirements: </span>
              <span v-if="parseFloat(adjustmentModel.adjustment || '0') !== 0">${{parseFloat(adjustmentModel.adjustment).toFixed(2)}}</span>
              <hr />
              <strong>Total: ${{price}}</strong>
              <div v-if="seller && sellerData.user.fee !== null">
                Artconomy service fee: -${{ fee }} <br />
                <strong>Your payout: ${{ payout }}</strong>
              </div>
            </div>
            <div class="pricing-container mt-2 pl-3 pr-3" v-if="seller && (newOrder || paymentPending) && (sellerData.user.fee !== null)">
              <ac-form-container
                  ref="adjustmentForm"
                  :schema="adjustmentSchema"
                  :model="adjustmentModel"
                  :options="adjustmentOptions"
                  :url="`${url}adjust/`"
                  method="PATCH"
                  :reset-after="false">
              </ac-form-container>
              <div class="text-xs-center">
                <v-btn type="submit" color="primary" @click.prevent="$refs.adjustmentForm.submit">Adjust price</v-btn><i v-if="$refs.adjustmentForm && $refs.adjustmentForm.saved" class="fa fa-check" style="color: green"></i>
              </div>
              <p class="mt-2">
                <strong>Note:</strong> Only one adjustment may be used. Therefore, please include all
                discounts and increases in the adjustment price. Be sure to comment so that the commissioner
                will see your reasoning. Do not approve a request until you have added your adjustment, as that
                will finalize the price.
              </p>
            </div>
          </v-flex>
          <v-flex xs12 class="pl-2 pr-2 pt-2 pb-3" text-xs-center :class="{'lg4': paymentDetail, 'md9': !paymentDetail, 'text-xs-center': !paymentDetail}">
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
            <div v-if="seller && queued">
              <p><strong>Awesome! The commissioner has sent payment.</strong></p>
              <p>You should start work on the commission as soon as you can. If there are revisions to upload, you may upload them (and the final, when ready) below.</p>
              <p>If for some reason you need to refund the customer, you may do so below. Note that refunding a customer has a $2.00 fee to cover costs with our payment processor.</p>
              <ac-action
                  variant="danger"
                  method="POST"
                  :url="`${this.url}refund/`"
                  :success="populateOrder"
                  class="refund-button"
              >
                Refund
              </ac-action>
            </div>
            <div v-if="buyer && queued && !justPaid">
              <p><strong>Your art has been queued!</strong></p>
              <p>We've received your payment and your work is now in the artist's queue. They'll start on it as soon as they're able, and will upload any agreed upon revisions for your review soon, or the final once it's ready.</p>
            </div>
            <div class="text-xs-center" v-if="newOrder || paymentPending">
              <ac-action class="cancel-order-button" :url="`${this.url}cancel/`" variant="danger" :success="populateOrder">Cancel</ac-action>
              <ac-action class="accept-order-btn" v-if="newOrder && seller" :confirm="true" :url="`${this.url}accept/`" variant="success" :success="populateOrder">
                Accept order
                <div class="text-left" slot="confirmation-text">
                  <p>
                    Are you sure you understand the commissioner's requirements? By accepting this order, you are confirming you
                    understand and agree to the <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement.</router-link>
                  </p>
                </div>
              </ac-action>
            </div>
            <div v-if="inProgress && seller">
              <p><strong>Here we go!</strong></p>
              <p>You've begun work on this piece. We've notified the commissioner that their piece is in progress and have sent them the link to your stream if you set one.</p>
              <p>If for some reason you need to refund the customer, you may do so below. Note that refunding a customer has a $2.00 fee to cover costs with our payment processor.</p>
              <ac-action
                  variant="danger"
                  method="POST"
                  :url="`${this.url}refund/`"
                  :success="populateOrder"
                  class="refund-button"
              >
                Refund
              </ac-action>
            </div>
            <div v-if="inProgress && buyer">
              <p><strong>Your art is on the way!</strong></p>
              <p>The artist has begun work on your commission. <a :href="order.stream_link" v-if="order.stream_link">They are streaming your piece here!</a></p>
            </div>
            <div v-if="(queued || inProgress) && seller">
              <div v-if="order.private">
                <p>
                  <strong>WARNING:</strong>
                  This order was marked as <strong>PRIVATE</strong>. Make sure any stream link you give is not publicly viewable! Be sure to add any extra access information in the comments.
                </p>
              </div>
              <form>
                <ac-form-container
                    method="PATCH"
                    ref="streamForm"
                    :url="`${this.url}start/`"
                    :model="streamModel"
                    :options="streamOptions"
                    :schema="streamSchema"
                    :success="populateOrder"
                    :reset-after="false">
                </ac-form-container>
                <div class="text-xs-center">
                  <v-btn type="submit" color="primary" @click.prevent="$refs.streamForm.submit"><span v-if="queued">Mark as In Progress</span><span v-else>Update Stream Link</span></v-btn><i v-if="$refs.streamForm && $refs.streamForm.saved" class="fa fa-check" style="color: green"></i>
                </div>
              </form>
            </div>
            <div v-if="cancelled">
              <strong>This order has been cancelled.</strong>
            </div>
            <div v-if="completed && buyer">
              <strong>Congratulations! Your order is complete</strong>
              <p>You can revisit this page at any time for your records.</p>
            </div>
            <div v-if="completed && seller">
              <strong>Congratulations! You've completed the order</strong>
              <p>You can revisit this page at any time for your records.</p>
            </div>
          </v-flex>
        </v-layout>
      </v-card>
      <v-card>
        <v-layout row wrap class="mt-3">
          <v-flex xs12 md6 v-if="buyer && paymentPending">
            <ac-card-manager
                ref="cardManager"
                :payment="true"
                :username="order.buyer.username"
                v-model="selectedCard"
            />
          </v-flex>
          <v-flex xs12 md6 text-xs-center class="mt-3 mb-3 pr-2 pl-2" v-if="buyer && paymentPending">
            <p><strong>Add a card or select a saved one on the left.</strong></p>
            <p>Once you've selected a card, you may click the pay button below to put the commission in the artist's queue.
              By paying, you are agreeing to the <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement.</router-link></p>
            <p>Artconomy is based in the United States of America</p>
            <div class="pricing-container" :class="{'text-xs-center': buyer && paymentPending}">
              <p v-if="order.status < 2">Price may be adjusted by the seller before finalization.</p>
              <span v-html="md.renderInline(order.product.name)"></span>: ${{order.price}}<br />
              <span v-if="adjustmentModel.adjustment < 0">Discount: </span>
              <span v-else-if="adjustmentModel.adjustment > 0">Custom requirements: </span>
              <span v-if="parseFloat(adjustmentModel.adjustment) !== 0">${{parseFloat(adjustmentModel.adjustment).toFixed(2)}}</span>
              <hr />
              <strong>Total: ${{price}}</strong>
              <div v-if="selectedCardModel && selectedCardModel.cvv_verified === false">
                <strong>Card Security code (CVV): </strong><v-text-field :autofocus="true" v-model="cvv" /> <br />
                <small>Three to four digit number, on the front of American Express cards, and on the back of all other cards.</small>
              </div>
              <div class="mt-2 text-xs-center">
                <ac-action class="pay-button" :disabled="selectedCard === null || !validCVV" :url="`${url}pay/`" variant="success" :send="paymentData" :success="postPay">Submit</ac-action>
              </div>
            </div>
          </v-flex>
          <v-flex xs12 text-xs-center v-if="justPaid" class="pr-2 pl-2">
            <i class="fa fa-5x fa-check-circle"></i><br />
            <p><strong>Your payment has been received!</strong></p>
            <p>We've received your payment and your work is now in the artist's queue. They'll start on it as soon as
              they're able, and will upload any agreed upon revisions for your review soon, or the final once it's ready.</p>
          </v-flex>
        </v-layout>
      </v-card>
      <v-card v-if="revisionsLimited && revisionsLimited.length">
        <v-layout row wrap>
          <v-flex xs12 class="pl-2">
            <h2>Revisions</h2>
          </v-flex>
        </v-layout>
      </v-card>
      <v-layout row wrap class="mt-3 pb-3 revisions-section" v-if="revisionsLimited && revisionsLimited.length">
        <v-flex xs12 md6 lg4 text-xs-center v-for="(revision, index) in revisionsLimited"
             class="order-revision"
             v-bind:key="revision.id">
          <ac-asset thumb-name="preview" img-class="max-width" :asset="revision" />
          <div class="text-xs-center text-section p-3 mt-2">
            Revision {{ index + 1 }} on {{ formatDate(revision.created_on) }}
            <ac-action
                v-if="seller && (index === revisionsLimited.length - 1) && !final"
                variant="danger"
                method="DELETE"
                :url="`${url}/revisions/${revision.id}/`"
                :success="reload"
            >
              <i class="fa fa-trash-o"></i>
            </ac-action>
          </div>
        </v-flex>
      </v-layout>
      <v-card v-if="final">
        <v-layout row wrap>
          <v-flex xs12 text-xs-center>
            <h2>Final</h2>
          </v-flex>
        </v-layout>
      </v-card>
      <v-layout row wrap class="mt-3 pb-3" v-if="final">
        <v-flex xs12 text-xs-center>
          <router-link v-if="output" :to="{name: 'Submission', params: {assetID: output.id}}">
            <ac-asset class="final-preview" thumb-name="preview" :asset="final" />
          </router-link>
          <ac-asset class="final-preview" v-else thumb-name="preview" :asset="final" />
          <div class="text-xs-center text-section pb-2">
            Final delivered {{ formatDate(final.created_on)}}
            <ac-action
                v-if="seller && review"
                variant="danger"
                method="DELETE"
                :url="`${this.url}revisions/${final.id}/`"
                :success="reload"
            >
              <i class="fa fa-trash-o"></i>
            </ac-action>
            <div v-if="(review || disputed) && seller">
              <p v-if="review">
                Waiting on the commissioner to approve the final result.
              </p>
              <div v-if="disputed">
                <strong>This order is under dispute</strong>
                <p>An Artconomy staff member will assist in dispute resolution. Please await further instruction in the comments.</p>
                <p>You may elect to refund to close the dispute early. We recommend waiting for our staff to review, however.</p>
                <p>Refunding a transaction has a fee of $2.00 to cover costs with our payment processor.</p>
                <ac-action
                    variant="danger"
                    method="POST"
                    :url="`${this.url}refund/`"
                    :success="populateOrder"
                    class="refund-button"
                >
                  Refund
                </ac-action>
              </div>
            </div>
            <div v-if="(review || disputed) && buyer">
              <ac-action
                variant="danger"
                method="POST"
                :url="`${this.url}dispute/`"
                :success="populateOrder"
                v-if="!disputed"
                class="dispute-button"
                >
                File Dispute
              </ac-action>
              <div v-else class="mt-2">
                <p>
                  We're sorry you are not satisfied. Our staff has been contacted about your dispute.
                  They will comment once they have reviewed your case. Please follow their instructions to allow for
                  a prompt resolution.
                </p>
                <p>
                  If you started this dispute in error, or if the artist has resolved the issues you have raised, you
                  may hit the approve button to close the dispute early.
                </p>
              </div>
              <ac-action
                  variant="success"
                  method="POST"
                  :url="`${this.url}approve/`"
                  :success="newSubmission"
                  class="approve-button"
              >
                Approve Result
              </ac-action>
            </div>
          </div>
        </v-flex>
      </v-layout>
      <v-layout row wrap text-xs-center class="mt-3 pb-3 revision-upload" v-if="showRevisionPanel">
        <v-flex xs12 md6 offset-md3>
          <form>
            <ac-form-container
                method="POST"
                ref="revisionForm"
                :url="`${this.url}revisions/`"
                :model="revisionModel"
                :options="revisionOptions"
                :schema="revisionSchema"
                :success="reload"
                v-if="seller && inProgress && revisionsRemain">
            </ac-form-container>
            <div class="text-xs-center">
              <v-btn type="submit" color="primary" v-if="seller && inProgress && revisionsRemain" @click.prevent="$refs.revisionForm.submit"><span v-if="(revisions.length < order.revisions)">Upload Revision</span><span v-else>Upload Final</span></v-btn>
            </div>
          </form>
        </v-flex>
      </v-layout>
    </v-container>
    <v-container fluid>
      <v-layout row wrap class="mt-3">
        <v-flex xs12>
          <ac-comment-section :commenturl="commenturl" :nesting="false" />
        </v-flex>
      </v-layout>
    </v-container>
    <v-container>
      <v-layout row wrap class="row" v-if="!order">
        <v-flex xs12 text-xs-center><i class="fa fa-spin fa-spinner fa-5x"></i></v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
  import VueFormGenerator from 'vue-form-generator'
  import AcCharacterPreview from './ac-character-preview'
  import AcAction from './ac-action'
  import AcCommentSection from './ac-comment-section'
  import AcAvatar from './ac-avatar'
  import AcPatchfield from './ac-patchfield'
  import AcAsset from './ac-asset'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import { artCall, md, ratings, formatDate } from '../lib'
  import AcFormContainer from './ac-form-container'
  import AcCardManager from './ac-card-manager'

  export default {
    name: 'Order',
    props: ['orderID'],
    components: {
      AcCardManager,
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
        let oldStream = this.order && this.order.stream_link
        this.order = response
        if (oldAdjustment === null) {
          this.adjustmentModel.adjustment = response.adjustment
        }
        if (oldStream === null) {
          this.streamModel.stream_link = response.stream_link
        }
        this.$root.$setUser(response.seller.username, this.sellerData, this.$error)
      },
      populateRevisions (response) {
        this.revisions = response.results
      },
      reload () {
        // The number of revisions can have effects on the order's status. Safer to let the server handle it.
        artCall(this.url, 'GET', undefined, this.populateOrder, this.$error)
        artCall(`${this.url}revisions/`, 'GET', undefined, this.populateRevisions, this.$error)
      },
      postPay (response) {
        this.justPaid = true
        this.populateOrder(response)
      },
      newSubmission (response) {
        this.$router.push({name: 'Submission', params: {'assetID': response.outputs[0].id}, query: {editing: 1}})
        this.populateOrder(response)
      },
      formatDate
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
      inProgress () {
        return this.order.status === 4
      },
      review () {
        return this.order.status === 5
      },
      cancelled () {
        return this.order.status === 6
      },
      disputed () {
        return this.order.status === 7
      },
      completed () {
        return this.order.status === 8
      },
      orderClosed () {
        return (this.completed || this.cancelled)
      },
      output () {
        return this.order.outputs[0]
      },
      showRevisionPanel () {
        return this.seller && this.revisionsRemain && !this.queued && !this.newOrder && !this.paymentPending
      },
      revisionsLimited () {
        if (this.revisionsRemain) {
          return this.revisions
        } else if (this.finalUploaded) {
          return this.revisions.slice(0, -1)
        } else {
          return this.revisions
        }
      },
      final () {
        if (this.finalUploaded) {
          console.log(this.revisions[this.revisions.length - 1])
          return this.revisions[this.revisions.length - 1]
        } else {
          return null
        }
      },
      finalUploaded () {
        return (this.revisions && (this.revisions.length > this.order.revisions))
      },
      revisionsRemain () {
        return (this.revisions && (this.revisions.length <= this.order.revisions))
      },
      validCVV () {
        if (this.$refs.cardManager.selectedCardModel && this.$refs.cardManager.selectedCardModel.cvv_verified === true) {
          return true
        }
        return RegExp('^\\d{3,4}$').test(this.cvv)
      },
      paymentDetail () {
        return this.seller || this.newOrder
      },
      price () {
        return (parseFloat(this.order.price) + parseFloat(this.adjustmentModel.adjustment || '0')).toFixed(2)
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
      },
      paymentData () {
        return {
          card_id: this.selectedCard,
          amount: this.price,
          cvv: this.cvv
        }
      }
    },
    data () {
      return {
        order: null,
        commenturl: `/api/sales/v1/order/${this.orderID}/comments/`,
        url: `/api/sales/v1/order/${this.orderID}/`,
        md: md,
        sellerData: {user: {fee: null}},
        selectedCard: null,
        selectedCardModel: null,
        justPaid: false,
        revisions: null,
        cvv: '',
        adjustmentModel: {
          adjustment: 0.00
        },
        revisionModel: {
          file: [],
          rating: null
        },
        streamModel: {
          stream_link: null
        },
        revisionSchema: {
          fields: [{
            type: 'v-select',
            label: 'Rating',
            model: 'rating',
            featured: true,
            required: true,
            values: ratings,
            hint: 'The content rating of this revision',
            selectOptions: {
              hideNoneSelectedText: true
            },
            validator: VueFormGenerator.validators.required
          }, {
            type: 'v-file-upload',
            id: 'file',
            label: 'File',
            model: 'file',
            required: true,
            validator: VueFormGenerator.validators.required
          }]
        },
        streamSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            model: 'stream_link',
            label: 'Link to stream (if applicable)',
            featured: true,
            validator: VueFormGenerator.validators.url
          }]
        },
        adjustmentSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'number',
            step: '.01',
            model: 'adjustment',
            label: 'Adjustment (USD)',
            featured: true
          }]
        },
        adjustmentOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        revisionOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        streamOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    watch: {
      selectedCard () {
        this.selectedCardModel = this.$refs.cardManager.selectedCardModel
      }
    },
    created () {
      this.reload()
      window.order = this
    }
  }
</script>

<style>
  .pricing-container {
    display: inline-block;
    text-align: left;
  }
</style>