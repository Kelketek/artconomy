<template>
  <div>
    <v-container v-if="order">
      <v-card>
        <v-layout row wrap>
          <v-flex xs12 md6 lg4 text-xs-center class="pt-2 pb-2 pl-2 pr-2">
            <router-link :to="{name: 'Product', params: {productID: order.product.id, username: order.product.user.username}}">
              <ac-asset :asset="order.product" thumb-name="preview" img-class="bound-image" />
            </router-link>
          </v-flex>
          <v-flex xs12 md6 class="pt-3 pl-2 pr-2">
            <router-link :to="{name: 'Product', params: {productID: order.product.id, username: order.product.user.username}}">
              <h1 v-html="mdRenderInline(order.product.name)"></h1>
            </router-link>
            <h2>Order #{{order.id}}</h2>
            <div v-html="mdRender(order.product.description)"></div>
            <div>
              <h4>Details:</h4>
              <div class="order-details" v-html="mdRender(order.details)"></div>
            </div>
            <div v-if="order.private">
              <p><strong>PRIVATE ORDER</strong></p>
            </div>
          </v-flex>
          <v-flex xs12 lg2 text-xs-center class="pt-3">
            <div class="text-xs-center">
              <h3>Ordered By</h3>
              <ac-avatar :user="order.buyer" :show-rating="true" />
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
    <v-container v-if="order && order.characters.length" grid-list-md>
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
      <v-card class="mt-3">
        <v-card-text>
          <v-layout row wrap>
            <v-flex xs3 sm1 v-if="order.escrow_disabled">
              <v-icon large class="yellow--text">warning</v-icon>
            </v-flex>
            <v-flex xs3 sm1 v-else>
              <v-icon large class="green--text">fa-shield</v-icon>
            </v-flex>
            <v-flex xs9 sm11 text-xs-center v-if="order.escrow_disabled">
              This order is not protected by
              <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
                Artconomy Shield.
              </router-link>
              Artconomy gives no guarantees on products ordered without Artconomy Shield, and <em><strong>ordering is at your own
              risk</strong></em>. <span v-if="price > 0">Your artist will instruct you on how to pay them.</span>
            </v-flex>
            <v-flex xs9 sm11 text-xs-center v-else>
              <p>
                This order is protected by
                <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
                  Artconomy Shield,
                </router-link> our escrow and dispute resolution service.
              </p>
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-card>
    </v-container>
    <v-container v-if="order && order.product.user.commission_info">
      <v-card>
        <v-layout row wrap>
          <v-flex xs12 v-html="mdRender(order.product.user.commission_info)" class="pl-2 pr-2"></v-flex>
        </v-layout>
      </v-card>
    </v-container>
    <v-container v-if="order">
      <v-card>
        <v-layout row wrap>
          <v-flex xs12 md6 lg2 text-xs-center class="pt-2">
            <h3>Seller:</h3>
            <ac-avatar :user="order.seller" :show-rating="true" />
          </v-flex>
          <v-flex xs12 md6 text-xs-center class="pt-2" v-if="paymentDetail">
            <div class="pricing-container">
              <p v-if="order.status < 2">Price may be adjusted by the seller before finalization.</p>
              <span v-html="mdRenderInline(order.product.name)"></span>: ${{order.price}}<br />
              <span v-if="adjustmentModel.adjustment < 0">Discount: </span>
              <span v-else-if="adjustmentModel.adjustment > 0">Custom requirements: </span>
              <span v-if="parseFloat(adjustmentModel.adjustment || '0') !== 0">${{parseFloat(adjustmentModel.adjustment).toFixed(2)}}</span>
              <hr />
              <strong>Total: ${{price}}</strong> <br />
              <strong>Expected Turnaround: {{turnaround}} days</strong>
              <div v-if="seller && sellerData.user.percentage_fee !== null">
                <span v-if="!order.escrow_disabled">Artconomy service fee: -${{ fee }} </span><br v-if="!order.escrow_disabled" />
                <strong v-if="!order.escrow_disabled">Your payout: ${{ payout }}</strong> <br v-if="!order.escrow_disabled" />
                <strong>Task weight: {{ weight }}</strong>
              </div>
            </div>
            <div class="pricing-container mt-2 pl-3 pr-3" v-if="seller && (newOrder || paymentPending) && (sellerData.user.percentage_fee !== null)">
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
                <v-btn type="submit" color="primary" @click.prevent="$refs.adjustmentForm.submit">Save Adjustments</v-btn><i v-if="$refs.adjustmentForm && $refs.adjustmentForm.saved" class="fa fa-check" style="color: green"></i>
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
              <p v-if="order.escrow_disabled"><strong>Be sure to let your customer know how to send you payment in the comments below!</strong></p>
              <div v-if="pricing">
                <div v-if="!landscape && !order.escrow_disabled">
                  You'll earn <strong>${{landscapeDifference}}</strong> more from this commission if you upgrade to Artconomy Landscape!
                  <br />
                  <v-btn :to="{name: 'Upgrade'}" color="purple">Upgrade Now!</v-btn>
                </div>
                <div v-else-if="!order.escrow_disabled">
                  Your Landscape subscription earns you <strong>${{landscapeDifference}}</strong> more than you would have earned on this commission otherwise!
                </div>
              </div>
            </div>
            <div v-if="seller && paymentPending">
              <p><strong>We've notified the commissioner of your acceptance!</strong></p>
              <p v-if="order.escrow_disabled">Make sure you've commented to let the commissioner know how to send payment to you. <strong>Hit the Mark Paid button below once you've received payment!</strong></strong></p>
              <p v-else>We will notify you once they have paid for the commission. You are advised not to begin work until payment has been received. If needed, you may adjust the pricing until the comissioner pays.</p>
            </div>
            <div v-if="buyer && paymentPending">
              <p><strong>The artist has accepted your commission! Please pay below.</strong></p>
              <p>Review the price and pay below. Once your payment has been received, your commission will be placed in the artist's queue.</p>
            </div>
            <div v-if="seller && queued">
              <p><strong>Awesome! The commissioner has sent payment.</strong></p>
              <p>You should start work on the commission as soon as you can. If there are revisions to upload, you may upload them (and the final, when ready) below.</p>
              <p v-if="price > 0">If for some reason you need to refund the customer, you may do so below. <span v-if="!order.escrow_disabled">Note that the cost of the refund fee is born by the commissioner and refunding may affect your rating.</span></p>
              <ac-action
                  variant="danger"
                  method="POST"
                  :url="`${this.url}refund/`"
                  :success="populateOrder"
                  class="refund-button"
                  :confirm="true"
              >
                <span v-if="order.escrow_disabled">Mark Refunded</span>
                <span v-else-if="price > 0">Refund</span>
                <span v-else>Cancel</span>
              </ac-action>
            </div>
            <div v-if="buyer && queued && !justPaid">
              <p><strong>Your art has been queued!</strong></p>
              <p>We've received your payment and your work is now in the artist's queue. They'll start on it as soon as they're able, and will upload any agreed upon revisions for your review soon, or the final once it's ready.</p>
            </div>
            <div class="text-xs-center" v-if="newOrder || paymentPending">
              <ac-action class="cancel-order-button" :url="`${this.url}cancel/`" variant="danger" :success="populateOrder">Cancel</ac-action>
              <ac-action class="accept-order-btn" v-if="paymentPending && seller && order.escrow_disabled" :confirm="true" :url="`${this.url}mark-paid/`" variant="success" :success="populateOrder">
                Mark Paid
                <div class="text-left" slot="confirmation-text">
                  <p>
                    Are you sure you understand the commissioner's requirements, and that you've received payment in the right amount? By accepting this order, you are confirming you
                    understand and agree to the <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement.</router-link>
                  </p>
                </div>
              </ac-action>
              <ac-action class="accept-order-btn" v-if="newOrder && seller" :confirm="true" :url="`${this.url}accept/`" variant="success" :success="populateOrder" method="PATCH" :send="adjustmentModel">
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
              <p>If for some reason you need to refund the commissioner, you may do so below. Note the cost of the refund fee is born by the customer, and refunding may affect your rating.</p>
              <ac-action
                  variant="danger"
                  method="POST"
                  :url="`${this.url}refund/`"
                  :success="populateOrder"
                  class="refund-button"
              >
                <span v-if="order.escrow_disabled">Mark Refunded</span>
                <span v-else>Refund</span>
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
              <p v-if="!order.escrow_disabled">
                If you have not yet set up your bank account, <router-link :to="{name: 'Settings', params: {tabName: 'payment', 'username': this.viewer.username, 'subTabName': 'disbursement'}}">
                you should do so now.</router-link>
              </p>
              <p v-if="!order.escrow_disabled">
                Your payment will be transferred to your bank account unless you've opted out of automatic withdrawal.
                It may take up to five business days to arrive, though it most commonly takes four.
              </p>
            </div>
            <div v-if="showDisputePeriod">
              <p>You may dispute this order for non-completion on {{formatDate(order.dispute_available_on)}}</p>
            </div>
            <div v-if="showDisputeForTime">
              <p>You may dispute this order for non-completion.</p>
              <ac-action
                  variant="danger"
                  method="POST"
                  color="red"
                  :url="`${this.url}dispute/`"
                  :success="populateOrder"
                  v-if="!disputed"
                  class="dispute-button"
              >
                File Dispute
              </ac-action>
            </div>
            <div v-if="disputed && !finalUploaded">
              <strong>This order is under dispute</strong>
              <p>An Artconomy staff member will assist in dispute resolution. Please await further instruction in the comments.</p>
              <p>You may elect to refund to close the dispute early. We recommend waiting for our staff to review, however.</p>
              <p>Note that the cost of the refund fee is born by the commissioner and refunding may affect your rating.</p>
              <p>
                <strong>Note:</strong>
                <span v-if="order.started_on">Work on this order started on {{formatDate(order.started_on)}}</span>
                <span v-else>Work has not started on this order.</span>
              </p>
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
              <span v-html="mdRenderInline(order.product.name)"></span>: ${{order.price}}<br />
              <span v-if="adjustmentModel.adjustment < 0">Discount: </span>
              <span v-else-if="adjustmentModel.adjustment > 0">Custom requirements: </span>
              <span v-if="parseFloat(adjustmentModel.adjustment) !== 0">${{parseFloat(adjustmentModel.adjustment).toFixed(2)}}</span>
              <hr />
              <strong>Total: ${{price}}</strong> <br />
              <strong>Expected Turnaround: {{turnaround}} days
                <span v-if="daysDifference"> ({{daysDifference}} days
                  <span v-if="daysDifference > 0">added</span>
                  <span v-else>removed</span>)
                </span>
              </strong>
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
            Revision {{ index + 1 }} on {{ formatDateTime(revision.created_on) }}
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
            Final delivered {{ formatDateTime(final.created_on)}}
            <ac-action
                v-if="seller && (review || order.escrow_disabled)"
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
                <p>Note that the cost of the refund fee is born by the commissioner and refunding may affect your rating.</p>
                <p>
                  <strong>Note:</strong>
                  <span v-if="order.started_on">Work on this order started on {{formatDate(order.started_on)}}</span>
                  <span v-else>Work has not started on this order.</span>
                </p>
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
                color="red"
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
                  :success="populateOrder"
                  class="approve-button"
              >
                Approve Result
              </ac-action>
              <p v-if="review">This order will auto-finalize on {{formatDate(order.auto_finalize_on)}}.</p>
            </div>
            <v-expansion-panel v-model="expandRating" v-if="completed && (price > 0)">
              <v-expansion-panel-content class="text-xs-center">
                <div slot="header">Rate Performance</div>
                <v-card class="mb-2">
                  <v-card-text class="pb-2">
                    <v-flex v-if="buyer">
                      <h2>Rate {{order.seller.username}}!</h2>
                      <ac-rating :url="`/api/sales/v1/order/${order.id}/rating/?end=buyer`" />
                    </v-flex>
                    <v-flex v-if="seller">
                      <h2>Rate {{order.buyer.username}}!</h2>
                      <ac-rating :url="`/api/sales/v1/order/${order.id}/rating/?end=seller`" />
                    </v-flex>
                  </v-card-text>
                </v-card>
              </v-expansion-panel-content>
            </v-expansion-panel>
            <div v-if="completed && buyer && !order.outputs.length">
              <v-btn @click="showPublish = true" color="primary">Add to Gallery!</v-btn>
              <ac-form-dialog
                  ref="publishForm" :schema="publishSchema" :model="publishModel"
                  :options="revisionOptions" :success="newSubmission"
                  v-model="showPublish"
                  :url="`/api/sales/v1/order/${order.id}/publish/`"
              />
            </div>
            <div v-else-if="order.outputs.length">
              <v-btn color="primary" :to="{name: 'Submission', params: {assetID: order.outputs[0].id}}">Visit Submission</v-btn>
            </div>
          </div>
        </v-flex>
      </v-layout>
      <v-layout row wrap text-xs-center class="mt-3 pb-3 revision-upload" v-if="showRevisionPanel">
        <v-flex xs12 md6 offset-md3>
          <h3 v-if="remainingUploads === 1">
            You need to upload the final piece below.
          </h3>
          <h3 v-else>
            You must upload {{ remainingUploads - 1 }} more revision<span v-if="remainingUploads > 2">s</span> and the final.
          </h3>
          <form>
            <ac-form-container
                method="POST"
                ref="revisionForm"
                :url="`${this.url}revisions/`"
                :model="revisionModel"
                :options="revisionOptions"
                :schema="revisionSchema"
                :success="reload"
                v-if="seller && (inProgress || disputed) && revisionsRemain">
            </ac-form-container>
            <div class="text-xs-center">
              <v-btn type="submit" color="primary" v-if="seller && (inProgress || disputed) && revisionsRemain" @click.prevent="$refs.revisionForm.submit"><span v-if="(revisions.length < order.revisions)">Upload Revision</span><span v-else>Upload Final</span></v-btn>
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
  import Markdown from '../mixins/markdown'
  import Perms from '../mixins/permissions'
  import {artCall, ratings, formatDateTime, EventBus, formatDate} from '../lib'
  import AcFormContainer from './ac-form-container'
  import AcCardManager from './ac-card-manager'
  import AcFormDialog from './ac-form-dialog'
  import AcRating from './ac-rating'
  import moment from 'moment'

  export default {
    name: 'Order',
    props: ['orderID'],
    components: {
      AcRating,
      AcFormDialog,
      AcCardManager,
      AcFormContainer,
      AcCharacterPreview,
      AcAvatar,
      AcPatchfield,
      AcAsset,
      AcCommentSection,
      AcAction
    },
    mixins: [Viewer, Perms, Markdown],
    methods: {
      populateOrder (response) {
        let oldOrder = this.order
        this.order = response
        if (oldOrder === null) {
          this.adjustmentModel.adjustment = response.adjustment
          this.adjustmentModel.adjustment_expected_turnaround = response.adjustment_expected_turnaround
          this.adjustmentModel.adjustment_task_weight = response.adjustment_task_weight
          this.streamModel.stream_link = response.stream_link
        }
        this.$root.$setUser(response.seller.username, this.sellerData, this.$error)
      },
      ratingClose () {
        this.expandRating = null
      },
      populateRevisions (response) {
        this.revisions = response.results
      },
      loadPricing (response) {
        this.pricing = response
      },
      reload () {
        // The number of revisions can have effects on the order's status. Safer to let the server handle it.
        artCall(this.url, 'GET', undefined, this.populateOrder, this.$error)
        artCall(`${this.url}revisions/`, 'GET', undefined, this.populateRevisions, this.$error)
        artCall('/api/sales/v1/pricing-info/', 'GET', undefined, this.loadPricing)
      },
      postPay (response) {
        this.justPaid = true
        this.populateOrder(response)
      },
      newSubmission (response) {
        this.$router.push({name: 'Submission', params: {'assetID': response.outputs[0].id}, query: {editing: 1}})
        this.populateOrder(response)
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
      disputeTimePossible () {
        if (!this.buyer) {
          return false
        }
        return (this.inProgress || this.queued)
      },
      showDisputePeriod () {
        if (!this.disputeTimePossible) {
          return false
        }
        return moment() < moment(this.order.dispute_available_on)
      },
      showDisputeForTime () {
        if (!this.disputeTimePossible) {
          return false
        }
        return moment() >= moment(this.order.dispute_available_on)
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
      remainingUploads () {
        return (this.order.revisions + 1) - this.revisions.length
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
        if (this.order.escrow_disabled) {
          return 0
        }
        return ((this.price * (this.sellerData.user.percentage_fee * 0.01)) + parseFloat(this.sellerData.user.static_fee)).toFixed(2)
      },
      payout () {
        return (this.price - this.fee).toFixed(2)
      },
      landscapeDifference () {
        if (this.order.escrow_disabled) {
          return 0
        }
        let standardFee = ((this.price * (this.pricing.standard_percentage * 0.01)) + parseFloat(this.pricing.standard_static)).toFixed(2)
        let landscapeFee = ((this.price * (this.pricing.landscape_percentage * 0.01)) + parseFloat(this.pricing.landscape_static)).toFixed(2)
        return (parseFloat(standardFee) - parseFloat(landscapeFee)).toFixed(2)
      },
      weight () {
        let weight = this.order.task_weight || this.order.product.task_weight
        return parseInt(weight) + parseInt(this.adjustmentModel.adjustment_task_weight || '0')
      },
      turnaround () {
        let turnaround = parseFloat(this.order.expected_turnaround) || parseFloat(this.order.product.expected_turnaround)
        return Math.ceil(parseFloat(turnaround) + parseFloat(this.adjustmentModel.adjustment_expected_turnaround || '0'))
      },
      daysDifference () {
        return this.turnaround - Math.ceil(this.order.expected_turnaround || this.order.product.expected_turnaround)
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
        formatDateTime,
        formatDate,
        sellerData: {user: {fee: null}},
        selectedCard: null,
        selectedCardModel: null,
        justPaid: false,
        revisions: null,
        expandRating: 0,
        cvv: '',
        publishModel: {
          title: '',
          caption: ''
        },
        pricing: null,
        showPublish: false,
        publishSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'Title',
            model: 'title',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'v-text',
            label: 'Caption',
            model: 'caption',
            featured: true,
            multiLine: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }]
        },
        adjustmentModel: {
          adjustment: 0.00,
          adjustment_expected_turnaround: 0.00,
          adjustment_task_weight: 0
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
            label: 'Surcharges/Discounts (USD)',
            featured: true
          }, {
            type: 'v-text',
            inputType: 'number',
            step: '.01',
            model: 'adjustment_expected_turnaround',
            label: 'Additional days required',
            featured: true,
            hint: 'Value is always rounded up when displaying to customer'
          }, {
            type: 'v-text',
            inputType: 'number',
            step: 1,
            model: 'adjustment_task_weight',
            label: 'Additional task weight',
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
      EventBus.$on('rating-submitted', this.ratingClose)
    },
    destroyed () {
      EventBus.$off('rating-submitted', this.ratingClose)
    }
  }
</script>

<style>
  .pricing-container {
    display: inline-block;
    text-align: left;
  }
</style>