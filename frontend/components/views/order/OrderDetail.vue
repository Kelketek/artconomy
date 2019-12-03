<template>
  <ac-load-section :controller="order">
    <template v-slot:default>
      <v-layout row wrap>
        <v-flex xs12 md3 lg2 pa-1 order-xs1>
          <v-toolbar dense>
            <ac-avatar :user="order.x.seller" :show-name="false"></ac-avatar>
            <v-toolbar-title>{{order.x.seller.username}}</v-toolbar-title>
          </v-toolbar>
          <v-card :color="$vuetify.theme.darkBase.darken2">
            <v-card-text>
              <v-layout row wrap>
                <v-flex xs12 title>
                  <span v-if="isSeller">Sale</span>
                  <span v-else-if="isArbitrator">Case</span>
                  <span v-else>Order</span>
                  #{{order.x.id}}
                </v-flex>
                <v-flex xs12 py-2 subheading>
                  {{name}}
                </v-flex>
                <v-flex xs12>
                  <ac-asset :asset="order.x.display" thumb-name="thumbnail"></ac-asset>
                </v-flex>
                <v-flex subheading class="py-2" v-if="is(NEW)">
                  Base Price: ${{product.price.toFixed(2)}}
                </v-flex>
                <v-flex xs12 v-if="is(NEW)">
                  <span v-if="revisionCount">
                    <strong>{{revisionCount}}</strong> revision<span v-if="revisionCount > 1">s</span> included.
                  </span><br v-if="revisionCount" />
                  <span>Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong></span><br />
                </v-flex>
                <v-flex xs12 class="pt-2">
                  <v-layout column>
                    <v-flex v-if="isStaff">
                      <v-select
                          v-model="viewMode"
                          :items="viewerItems"
                          label="View as..."
                          outline
                          class="view-mode-select"
                      ></v-select>
                    </v-flex>
                  </v-layout>
                </v-flex>
                <v-flex xs12 class="pt-2">
                  <ac-escrow-label :escrow="escrow" name="order" />
                </v-flex>
              </v-layout>
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex xs12 md6 lg7 pa-1 order-xs3 order-md2>
          <v-layout row wrap>
            <v-flex xs12>
              <v-toolbar dense v-if="buyer">
                <ac-avatar :username="buyer.username" :show-name="false"></ac-avatar>
                <v-toolbar-title>{{deriveDisplayName(buyer.username)}}</v-toolbar-title>
              </v-toolbar>
              <v-card>
                <v-card-text>
                  <v-layout row wrap>
                    <v-flex shrink>
                      <h2>Details:</h2>
                    </v-flex>
                    <v-flex text-xs-right grow>
                      <v-chip color="white" light v-if="order.x.private">
                        <v-icon left>visibility_off</v-icon>
                        Private
                      </v-chip>
                      <ac-order-status :order="order.x"></ac-order-status>
                      <v-btn class="mx-0 rating-button" small :color="ratingColor[order.x.rating]" :ripple="false">
                        {{ratingsShort[order.x.rating]}}
                      </v-btn>
                    </v-flex>
                  </v-layout>
                  <ac-rendered :value="order.x.details"></ac-rendered>
                  <v-flex v-if="!buyer" xs12>
                    <ac-form @submit.prevent="orderEmail.submitThen(markInviteSent)">
                    <ac-form-container v-bind="orderEmail.bind">
                      <v-layout row justify-content align-content-center>
                        <v-flex>
                          <ac-patch-field
                            label="Customer email address"
                            hint="Set and save this to send the customer an invite link."
                            :persistent-hint="true"
                            :patcher="order.patchers.customer_email"
                            :refresh="false"
                          ></ac-patch-field>
                        </v-flex>
                        <v-flex shrink pl-2 d-flex align-self-center>
                          <v-btn
                            :disabled="inviteDisabled"
                            color="primary"
                            type="submit"
                            class="send-invite-button"
                          >Send Invite Link</v-btn>
                        </v-flex>
                      </v-layout>
                      <v-layout row wrap>
                        <v-flex xs12>
                          <v-alert v-model="inviteSent" :dismissible="true" type="success">
                            Invite email sent!
                          </v-alert>
                        </v-flex>
                      </v-layout>
                    </ac-form-container>
                    </ac-form>
                  </v-flex>
                  <v-subheader v-if="commissionInfo">Commission Info</v-subheader>
                  <ac-rendered :value="commissionInfo" :truncate="200"></ac-rendered>
                </v-card-text>
              </v-card>
            </v-flex>
            <v-flex xs12 v-if="characters.list.length">
              <v-card-text>
                <ac-load-section :controller="characters">
                  <template v-slot:default>
                    <ac-character-display :controller="characters" :editable="false"></ac-character-display>
                  </template>
                </ac-load-section>
              </v-card-text>
            </v-flex>
            <v-flex xs12>
              <ac-revision-manager
                  :list="revisions" :is-seller="isSeller || isArbitrator"
                  :order="order"
                  :hidden="order.x.revisions_hidden"
                  :archived="(is(COMPLETED) || is(REFUNDED) || is(CANCELLED)) && !order.x.escrow_disabled"
                  @finalize="statusEndpoint('complete')()"
                  @reopen="statusEndpoint('reopen')()"
                  :revision-count="revisionCount"
              ></ac-revision-manager>
            </v-flex>
            <v-flex xs12 v-if="isBuyer && is(REVIEW)" text-xs-center>
              <v-btn color="primary" @click="statusEndpoint('approve')()">Approve Final</v-btn>
              <v-btn color="danger" @click="statusEndpoint('dispute')()">File Dispute</v-btn>
            </v-flex>
            <v-flex xs12 v-if="isBuyer && is(DISPUTED)" text-xs-center pt-2>
              <p><strong>Your dispute has been filed.</strong> Please stand by for further instructions.
                If you are able to work out your disagreement with the artist, please approve the order using the
                button below.</p>
              <ac-confirmation :action="statusEndpoint('approve')">
                <template v-slot:default="{on}">
                  <v-btn color="primary" v-on="on">Approve Final</v-btn>
                </template>
              </ac-confirmation>
            </v-flex>
            <v-flex xs12 sm6 md8 v-if="isBuyer && (is(COMPLETED) || is(REFUNDED))" d-flex>
              <ac-order-rating end="seller" :order-id="orderId" key="seller"></ac-order-rating>
            </v-flex>
            <v-flex xs12 v-if="buyer && isSeller && (is(COMPLETED) || is(REFUNDED))">
              <ac-order-rating end="buyer" :order-id="orderId" key="buyer"></ac-order-rating>
            </v-flex>
            <v-flex v-if="isBuyer && is(COMPLETED)" xs12 sm6 md4 text-xs-center pt-2>
              <v-img src="/static/images/fridge.png" max-height="20vh" contain></v-img>
              <v-btn v-if="buyerSubmission" color="primary"
                     :to="{name: 'Submission', params: {submissionId: buyerSubmission.x.id}}">Visit in Collection</v-btn>
              <v-btn color="green" v-else @click="addToCollection" class="collection-add">Add to my Collection</v-btn>
            </v-flex>
            <v-flex xs12>
              <ac-comment-section :commentList="comments" :nesting="false" :locked="!isInvolved" :guest-ok="true" :show-history="isArbitrator"></ac-comment-section>
            </v-flex>
          </v-layout>
        </v-flex>
        <v-flex xs12 md3 lg3 pa-1 order-xs2 order-md3>
          <v-card>
            <v-card-title><h3>Now what?</h3></v-card-title>
            <ac-form>
            <ac-form-container @submit.prevent="stateChanger" :errors="stateChange.errors" :sending="stateChange.sending">
            <v-card-text>
              <v-layout row wrap>
                <v-flex v-if="is(NEW) && isBuyer" xs12>
                  <p>Your order has been placed and is awaiting the artist's review. You will receive an email when the
                    artist has accepted or rejected the order, or if they have any comments.</p>
                  <p>You may add additional comments or questions below!</p>
                </v-flex>
                <v-flex v-if="is(NEW) && isSeller" xs12>
                  <p>This order is pending your review. Please make any pricing adjustments and accept the order, or
                    reject the order if you are unwilling or unable to complete the piece.</p>
                  <p>You may add comments to ask the commissioner questions.</p>
                </v-flex>
                <v-flex v-if="!is(COMPLETED) && !isRegistered" :to="registerLink" xs12 text-xs-center>
                  <v-btn color="green" :to="registerLink" class="link-account">Link an Account</v-btn>
                </v-flex>
                <v-flex v-if="(is(NEW) && isSeller) || !(is(NEW) || is(CANCELLED))" xs12 pb-2>
                  <ac-price-preview
                      :price="order.x.price"
                      :adjustment="order.x.adjustment"
                      :username="order.x.seller.username"
                      :is-seller="isSeller"
                      :escrow="!order.x.escrow_disabled"
                  ></ac-price-preview>
                  <v-divider></v-divider>
                  Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong><br />
                  <span v-if="revisionCount">Revisions: <strong>{{revisionCount}}</strong></span><br v-if="revisionCount" />
                  <span v-if="isSeller">AWOO Task Weight: <strong>{{taskWeight}}</strong></span>
                </v-flex>
                <v-flex xs12 v-if="(is(NEW) || is(PAYMENT_PENDING)) && isSeller">
                  <v-layout row wrap>
                    <v-flex xs12>
                      <ac-patch-field
                          :patcher="order.patchers.adjustment"
                          field-type="ac-price-field"
                          label="Surcharges/Discounts (USD)"
                      ></ac-patch-field>
                    </v-flex>
                    <v-flex xs12>
                      <ac-patch-field
                          :patcher="order.patchers.adjustment_expected_turnaround"
                          label="Additional Days Required"
                      ></ac-patch-field>
                    </v-flex>
                    <v-flex xs12>
                      <ac-patch-field
                        :patcher="order.patchers.adjustment_revisions"
                        label="Additional Revisions Offered"
                      ></ac-patch-field>
                    </v-flex>
                    <v-flex xs12>
                      <ac-patch-field
                          :patcher="order.patchers.adjustment_task_weight"
                          label="Additional task weight"
                      ></ac-patch-field>
                    </v-flex>
                    <v-flex xs12 text-xs-center>
                      <ac-confirmation :action="statusEndpoint('accept')" v-if="is(NEW)">
                        <template v-slot:default="{on}">
                          <v-btn v-on="on" color="green" class="accept-order">Accept Order</v-btn>
                        </template>
                        <v-flex slot="confirmation-text">
                          I understand the commissioner's requirements, and I agree to be bound by the
                          <router-link :to="{name: 'CommissionAgreement'}">Commission agreement</router-link>.
                        </v-flex>
                        <span slot="title">Accept Order</span>
                        <span slot="confirm-text">I agree</span>
                      </ac-confirmation>
                    </v-flex>
                  </v-layout>
                </v-flex>
                <ac-escrow-label :escrow="!order.x.escrow_disabled" v-if="is(PAYMENT_PENDING) && isBuyer" name="order"></ac-escrow-label>
                <v-flex v-if="is(PAYMENT_PENDING) && isBuyer" xs12>
                  <v-divider />
                  <p>
                    <strong>Congratulations!</strong> Your artist has accepted your order. Please submit payment so that it can be added to their work queue.
                    <span v-if="order.x.escrow_disabled">Your artist will inform you on how to pay them.</span>
                  </p>
                  <p v-if="!order.x.escrow_disabled">
                    <strong class="danger">WARNING:</strong> Only send payment using the '<strong>Send Payment</strong>' button directly below this paragraph.
                    Do not use any other method, button, or link, or we will not be able to protect you from fraud. If your
                    artist asks for payment using another method, or if you are getting errors, please <a @click="setSupport(true)">contact support.</a>
                  </p>
                </v-flex>
                <v-flex v-if="is(PAYMENT_PENDING) && isBuyer && !order.x.escrow_disabled" text-xs-center xs12 payment-section>
                  <v-btn color="green" @click="showPayment = true" class="payment-button">Send Payment</v-btn>
                  <ac-form-dialog v-model="showPayment" @submit.prevent="paymentForm.submitThen(updateOrder)" :large="true" v-bind="paymentForm.bind">
                    <v-layout row wrap>
                      <v-flex xs12 text-xs-center>Total Charge: <strong>${{totalCharge.toFixed(2)}}</strong></v-flex>
                      <v-flex xs12>
                        <ac-card-manager
                            ref="cardManager"
                            :payment="true"
                            :username="buyer.username"
                            :cc-form="paymentForm"
                            :field-mode="true"
                            v-model="paymentForm.fields.card_id.model"
                        />
                      </v-flex>
                      <v-flex xs12 text-xs-center>
                        <p>Use of Artconomy is subject to the
                          <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>.<br />
                          This order is subject to the <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement</router-link>.<br />
                          Artconomy is based in the United States of America.</p>
                      </v-flex>
                    </v-layout>
                  </ac-form-dialog>
                </v-flex>
                <v-flex v-if="isBuyer && order.x.stream_link && !(is(COMPLETED) || is(CANCELLED) || is(REFUNDED))" xs12>
                  <p><a :href="order.x.stream_link" target="_blank">Your artist is streaming your commission here!</a></p>
                </v-flex>
                <v-flex v-if="is(PAYMENT_PENDING) && isSeller" xs12>
                  <p>The commissioner has been informed that they must now pay in order for you to work on the order.
                    You may continue to comment and tweak pricing in the interim, or you may cancel the order if you need to.</p>
                  <p v-if="order.x.escrow_disabled">
                    <strong>REMEMBER:</strong> As we are not handling payment for this order, you MUST tell your
                    commissioner how to pay you. Leave a comment telling them how if you have not done so already.
                    When the customer has paid, click the 'Mark Paid' button.</p>
                  <p v-else>
                    You may mark this order as paid, if the customer has paid you through an outside method, or you wish to waive payment for this commission.
                  </p>
                  <v-flex text-xs-center v-if="order.x.escrow_disabled">
                    <v-btn color="primary" @click="statusEndpoint('mark-paid')()">Mark Paid</v-btn>
                  </v-flex>
                  <ac-confirmation :action="statusEndpoint('mark-paid')" v-else>
                    <template v-slot:default="{on}">
                      <v-flex text-xs-center xs12>
                        <v-btn color="primary" v-on="on">Mark Paid</v-btn>
                      </v-flex>
                    </template>
                    <v-flex slot="confirmation-text">
                      <p>Artconomy will not be able to protect you from fraud if your customer has paid through an outside
                        method.</p>
                      <p><strong>Don't do this unless you really know what you're doing!</strong></p>
                        <p>If you are having trouble, please contact support.</p>
                    </v-flex>
                  </ac-confirmation>
                </v-flex>
                <v-flex v-if="isSeller && is(REVIEW)" xs12>
                  <p>The commissioner has been informed that the final is ready for their review. Please stand by for final approval!</p>
                </v-flex>
                <v-flex v-if="is(REVIEW)" xs12>
                  <p>This order will auto-finalize on <strong>{{formatDateTerse(order.x.auto_finalize_on)}}</strong>.</p>
                </v-flex>
                <v-flex v-if="isBuyer && is(REVIEW)" xs12>
                  <p>Your artist has completed the piece! If all is well, please hit approve. Otherwise, if there is an
                    issue you cannot resolve with the artist, please hit the dispute button.</p>
                  <v-flex text-xs-center>
                    <v-btn color="primary" @click="statusEndpoint('approve')()">Approve Final</v-btn>
                    <v-btn color="danger" @click="statusEndpoint('dispute')()">File Dispute</v-btn>
                  </v-flex>
                </v-flex>
                <v-flex xs12 v-if="isBuyer && is(DISPUTED)" text-xs-center pt-2>
                  <p><strong>Your dispute has been filed.</strong> Please stand by for further instructions.
                    If you are able to work out your disagreement with the artist, please approve the order using the
                    button below.</p>
                </v-flex>
                <v-flex v-if="(isBuyer || isArbitrator) && is(DISPUTED)" xs12 text-xs-center>
                  <ac-confirmation :action="statusEndpoint('approve')">
                    <template v-slot:default="{on}">
                      <v-btn color="primary" v-on="on">Approve Final</v-btn>
                    </template>
                  </ac-confirmation>
                </v-flex>
                <v-flex v-if="is(NEW) || is(PAYMENT_PENDING)" text-xs-center xs12>
                  <ac-confirmation :action="statusEndpoint('cancel')">
                    <template v-slot:default="{on}">
                      <v-btn v-on="on">Cancel</v-btn>
                    </template>
                  </ac-confirmation>
                </v-flex>
                <v-flex v-if="is(QUEUED) && isBuyer" xs12>
                  <p>Your order has been added to the artists queue. We will notify you when they have begun work!</p>
                </v-flex>
                <v-flex v-if="is(QUEUED) && isSeller" xs12>
                  <p><strong>Excellent!</strong> The commissioner has paid and the money is being held in safekeeping.
                    When you've started work, hit the 'Mark In Progress' button to let the customer know.
                    You can also set the order's streaming link (if applicable) here:</p>
                </v-flex>
                <v-flex v-if="order.x.dispute_available_on && !(is(DISPUTED) || is(REVIEW) || is(COMPLETED) || is(REFUNDED))" xs12>
                  <p v-if="disputeTimeElapsed">You may file dispute for non-completion if needed.</p>
                  <p v-else>This order may be disputed for non-completion on: <br /><strong>{{formatDateTerse(order.x.dispute_available_on)}}.</strong></p>
                  <v-flex text-xs-center>
                  <v-btn v-if="disputeTimeElapsed && isBuyer" @click="statusEndpoint('dispute')()" color="danger">File Dispute</v-btn>
                  </v-flex>
                </v-flex>
                <v-flex v-if="isSeller && (is(QUEUED) || is(IN_PROGRESS) || is(REVIEW) || is(DISPUTED))" xs12>
                  <v-alert :value="order.x.private">
                    <strong>NOTE:</strong> This user has asked that this commission be private. Please do not use a public streaming link!
                  </v-alert>
                  <ac-patch-field
                      :patcher="order.patchers.stream_link" label="Stream URL">
                  </ac-patch-field>
                </v-flex>
                <v-flex v-if="isBuyer && is(IN_PROGRESS)">
                  <p>The artist has begun work on your order. You'll be notified as they make progress!</p>
                </v-flex>
                <v-flex v-if="is(QUEUED) && isSeller" text-xs-center xs12>
                  <v-btn color="primary" @click="statusEndpoint('start')()">Mark In Progress</v-btn>
                </v-flex>
                <v-flex v-if="is(DISPUTED) && isSeller">
                  <p><strong>This order is under dispute.</strong> One of our staff will be along soon to give further
                    instruction. If you wish, you may refund the customer. Otherwise, please wait for our staff to work
                    with you and the commissioner on a resolution.</p>
                </v-flex>
                <v-flex v-if="(isSeller || isArbitrator) && (is(QUEUED) || is(IN_PROGRESS) || is(REVIEW) || is(DISPUTED))" xs12 text-xs-center>
                  <ac-confirmation :action="statusEndpoint('refund')">
                    <template v-slot:default="{on}">
                      <v-btn v-on="on">
                        <span v-if="escrow">Refund</span>
                        <span v-else>Mark Refunded</span>
                      </v-btn>
                    </template>
                  </ac-confirmation>
                </v-flex>
                <v-flex v-if="is(COMPLETED)" xs12 text-xs-center>
                  <p>This order has been completed! <strong>Thank you for using Artconomy!</strong></p>
                </v-flex>
                <v-flex v-if="is(REFUNDED)" xs12 text-xs-center>
                  <p>This order has been refunded and is now archived.</p>
                </v-flex>
                <v-flex v-if="isSeller && escrow && is(COMPLETED)" xs12 text-xs-center>
                  <p><router-link :to="{name: 'Payout', params: {username: seller.username}}">
                    If you have not already, please add your bank account in your payout settings.</router-link></p>
                  <p>A transfer will automatically be initiated to your bank account.
                    Please wait up to five business days for payment to post.</p>
                </v-flex>
                <v-flex v-if="isSeller && is(COMPLETED) && !order.x.private" xs12 text-xs-center>
                  <v-img src="/static/images/fridge.png" max-height="20vh" contain></v-img>
                  <v-btn v-if="sellerSubmission" color="primary"
                         :to="{name: 'Submission', params: {submissionId: sellerSubmission.x.id}}">Visit in Gallery</v-btn>
                  <v-btn color="green" v-else @click="showAddSubmission = true">Add to my Gallery</v-btn>
                </v-flex>
                <v-flex v-if="isBuyer && is(COMPLETED)" xs12 text-xs-center>
                  <v-btn v-if="buyerSubmission" color="primary"
                         :to="{name: 'Submission', params: {submissionId: buyerSubmission.x.id}}">Visit in Collection</v-btn>
                  <v-btn color="green" v-else @click="addToCollection" class="collection-add">Add to my Collection</v-btn>
                </v-flex>
                <v-flex v-if="is(CANCELLED) && isBuyer">
                  <p>This order has been cancelled. You will have to create a new order if you want a commission.</p>
                </v-flex>
                <v-flex v-if="is(CANCELLED) && isSeller">
                  <p>This order has been cancelled. There is nothing more to do.</p>
                </v-flex>
                <ac-form-dialog
                    v-if="is(COMPLETED)"
                    @submit.prevent="addSubmission.submitThen(visitSubmission)"
                    v-model="showAddSubmission"
                    :sending="addSubmission.sending"
                    :errors="addSubmission.errors"
                    v-bind="addSubmission.bind"
                    :large="true"
                    :title="isSeller ? 'Add to Gallery' : 'Add to Collection'"
                >
                  <v-container class="pa-0" grid-list-md>
                    <v-layout row wrap>
                      <v-flex xs12>
                        <ac-bound-field :field="addSubmission.fields.title" label="Title"></ac-bound-field>
                      </v-flex>
                      <v-flex xs12>
                        <ac-bound-field
                            :field="addSubmission.fields.caption"
                            field-type="ac-editor" :save-indicator="false"
                            label="Caption"
                            hint="Tell viewers a little about the piece."
                            :persistent-hint="true"
                        ></ac-bound-field>
                      </v-flex>
                      <v-flex xs12>
                        <ac-bound-field
                            :field="addSubmission.fields.tags" field-type="ac-tag-field" label="Tags"
                            hint="Add some tags to make this submission easier to manage. We've added all the tags of
                            the characters attached to this piece (if any) to help!"
                            :persistent-hint="true"
                        ></ac-bound-field>
                      </v-flex>
                      <v-flex xs12 sm6>
                        <ac-bound-field :field="addSubmission.fields.private" label="Private" field-type="v-checkbox"
                                        hint="If checked, will not show this submission to anyone you've not explicitly shared it with."
                        />
                      </v-flex>
                      <v-flex xs12 sm6>
                        <ac-bound-field :field="addSubmission.fields.comments_disabled" label="Comments Disabled" field-type="v-checkbox"
                                        hint="If checked, prevents others from commenting on this submission."
                        />
                      </v-flex>
                    </v-layout>
                  </v-container>
                </ac-form-dialog>
              </v-layout>
            </v-card-text>
            </ac-form-container>
            </ac-form>
          </v-card>
        </v-flex>
        <ac-expanded-property v-model="showConfirm">
          <span slot="title">We're on it!</span>
          <v-layout row wrap justify-content-center align-center class="order-confirmation">
            <v-flex xs12 sm6 md3 d-flex align-self-center>
              <v-img src="/static/images/cheering.png" :contain="true" max-height="30vh"></v-img>
            </v-flex>
            <v-flex xs12 sm6 md9 d-flex align-self-center>
              <v-flex>
                <h1>Order Placed.</h1>
                <h2>Check your email!</h2>
                <p>We've sent a confirmation to your email address. If you haven't received it, please check your spam folder.</p>
                <p>
                  <strong>It is very important that you verify you're getting emails from Artconomy, or else your artist
                    won't be able to send you messages on their progress.</strong> If you're having trouble,
                  <a href="#" @click.prevent="setSupport(true)">please contact support</a> or ask for help in the <a href="https://t.me/Artconomy" target="_blank">Artconomy Telegram group</a>.</p>
                <p>Your artist will contact you soon to confirm acceptance of your commission, or ask additional questions.</p>
              </v-flex>
            </v-flex>
          </v-layout>
        </ac-expanded-property>
      </v-layout>
    </template>
  </ac-load-section>
</template>
<script lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {ProfileController} from '@/store/profiles/controller'
import {SingleController} from '@/store/singles/controller'
import Order from '@/types/Order'
import {Prop, Watch} from 'vue-property-decorator'
import {User} from '@/store/profiles/types/User'
import AcProductPreview from '@/components/AcProductPreview.vue'
import AcAsset from '@/components/AcAsset.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'
import AcRendered from '@/components/wrappers/AcRendered'
import AcAvatar from '@/components/AcAvatar.vue'
import moment, {Moment} from 'moment-business-days'
import {ListController} from '@/store/lists/controller'
import AcCharacterDisplay from '@/components/views/submission/AcCharacterDisplay.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import Ratings from '@/mixins/ratings'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {FormController} from '@/store/forms/form-controller'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcPricePreview from '@/components/AcPricePreview.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {baseCardSchema} from '@/lib'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import Revision from '@/types/Revision'
import AcRevisionManager from '@/components/views/order/AcRevisionManager.vue'
import Submission from '@/types/Submission'
import AcBoundField from '@/components/fields/AcBoundField'
import AcOrderRating from '@/components/views/order/AcOrderRating.vue'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
import LinkedCharacter from '@/types/LinkedCharacter'
import {RawLocation} from 'vue-router'
import AcOrderStatus from '@/components/AcOrderStatus.vue'
import {Mutation} from 'vuex-class'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcForm from '@/components/wrappers/AcForm.vue'

enum VIEWER_TYPE {
  UNSET = 0,
  BUYER = 1,
  SELLER = 2,
  STAFF = 3,
}

@Component({components: {
  AcForm,
  AcExpandedProperty,
  AcOrderStatus,
  AcEscrowLabel,
  AcOrderRating,
  AcBoundField,
  AcRevisionManager,
  AcCardManager,
  AcFormDialog,
  AcConfirmation,
  AcPricePreview,
  AcPatchField,
  AcFormContainer,
  AcCommentSection,
  AcCharacterDisplay,
  AcAvatar,
  AcRendered,
  AcLink,
  AcAsset,
  AcProductPreview,
  AcLoadSection}})
export default class OrderDetail extends mixins(Viewer, Formatting, Ratings) {
  @Mutation('supportDialog') public setSupport: any
  @Prop({required: true})
  public orderId!: number
  public buyerHandler: ProfileController|null = null
  public sellerHandler: ProfileController = null as unknown as ProfileController
  public arbitratorHandler: ProfileController|null = null
  public order: SingleController<Order> = null as unknown as SingleController<Order>
  public characters: ListController<LinkedCharacter> = null as unknown as ListController<LinkedCharacter>
  public comments: ListController<Comment> = null as unknown as ListController<Comment>
  public revisions: ListController<Revision> = null as unknown as ListController<Revision>
  public outputs: ListController<Submission> = null as unknown as ListController<Submission>
  public stateChange: FormController = null as unknown as FormController
  public paymentForm: FormController = null as unknown as FormController
  public addSubmission: FormController = null as unknown as FormController
  public orderEmail: FormController = null as unknown as FormController
  public inviteSent = false
  public showPayment = false
  public showAddSubmission = false
  public showConfirm = false
  public viewMode = VIEWER_TYPE.UNSET
  public NEW = 1
  public PAYMENT_PENDING = 2
  public QUEUED = 3
  public IN_PROGRESS = 4
  public REVIEW = 5
  public CANCELLED = 6
  public DISPUTED = 7
  public COMPLETED = 8
  public REFUNDED = 9

  public ensureHandler(handler: ProfileController, user: User, loadProfile?: boolean) {
    if (!handler.user.x) {
      handler.user.setX(user)
      handler.user.ready = true
      // Make sure we get the full info since it's cached for other stuff.
      handler.user.get()
    }
    if (loadProfile) {
      /* istanbul ignore next */
      if (!handler.artistProfile.x) {
        handler.artistProfile.get()
      }
    }
  }

  @Watch('order.patchers.customer_email.model')
  public resetSent() {
    this.inviteSent = false
  }

  @Watch('order.x')
  public updateAmount(order: Order) {
    /* istanbul ignore if */
    if (!order) {
      return
    }
    this.paymentForm.fields.amount.update(this.totalCharge)
  }

  public get totalCharge() {
    const order = this.order.x as Order
    /* istanbul ignore if */
    if (!order) {
      return 0
    }
    return order.price + order.adjustment
  }

  public get viewerItems() {
    const items = [{text: 'Staff', value: VIEWER_TYPE.STAFF}]
    if (this.buyer) {
      items.push({text: 'Buyer', value: VIEWER_TYPE.BUYER})
    }
    items.push({text: 'Seller', value: VIEWER_TYPE.SELLER})
    return items
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
    if (!this.order.x) {
      return ''
    }
    return this.order.x.commission_info
  }

  @Watch('order.x.revisions_hidden')
  public fetchRevisions(newVal: boolean|undefined, oldVal: boolean|undefined) {
    if ((oldVal === true) && (newVal === false)) {
      this.revisions.get()
    }
  }

  @Watch('order.x.id')
  public prePopulate(newId: number|undefined, oldId: number|undefined) {
    const order = this.order.x as Order
    if (order.buyer) {
      // This order has a buyer.
      this.buyerHandler = this.$getProfile(order.buyer.username, {})
      this.ensureHandler(this.buyerHandler, order.buyer)
    }
    this.sellerHandler = this.$getProfile(order.seller.username, {})
    this.ensureHandler(this.sellerHandler, order.seller, true)
    if (order.arbitrator) {
      this.arbitratorHandler = this.$getProfile(order.arbitrator.username, {})
      this.ensureHandler(this.arbitratorHandler, order.arbitrator)
    }
    this.outputs.setList(order.outputs)
    this.outputs.fetching = false
    this.outputs.ready = true
    this.addSubmission.fields.private.update(order.private)
  }

  public get product() {
    /* istanbul ignore if */
    if (!this.order.x) {
      return null
    }
    if (!this.order.x.product) {
      return null
    }
    return this.order.x.product
  }

  public get inviteDisabled() {
    /* istanbul ignore if */
    if (!this.order.x) {
      return true
    }
    const value = this.order.patchers.customer_email.model
    return (this.inviteSent || !value || value !== this.order.x.customer_email)
  }

  public get disputeTimeElapsed() {
    const order = this.order.x as Order
    /* istanbul ignore if */
    if (!order) {
      return false
    }
    if (!order.dispute_available_on) {
      return false
    }
    // @ts-ignore
    return moment(order.dispute_available_on) < moment.now()
  }

  public get buyer() {
    if (!this.buyerHandler) {
      return null
    }
    return this.buyerHandler.user.x
  }

  public get seller() {
    /* istanbul ignore if */
    if (!this.sellerHandler) {
      return null
    }
    return this.sellerHandler.user.x
  }

  public get arbitrator() {
    if (!this.arbitratorHandler) {
      return null
    }
    return this.arbitratorHandler.user.x
  }

  public get isBuyer() {
    if (this.viewMode === VIEWER_TYPE.BUYER) {
      return true
    }
    if (this.viewMode !== VIEWER_TYPE.UNSET) {
      return false
    }
    return this.buyer && this.buyer.username === this.rawViewerName
  }

  public get isSeller() {
    if (this.viewMode === VIEWER_TYPE.SELLER) {
      return true
    }
    if (this.viewMode !== VIEWER_TYPE.UNSET) {
      return false
    }
    return this.seller && this.seller.username === this.rawViewerName
  }

  public get isArbitrator() {
    if (this.viewMode === VIEWER_TYPE.STAFF) {
      return true
    }
    if (this.viewMode !== VIEWER_TYPE.UNSET) {
      return false
    }
    return this.arbitrator && this.arbitrator.username === this.rawViewerName
  }

  public get isInvolved() {
    return this.isBuyer || this.isSeller || this.isArbitrator
  }

  public get name() {
    if (!this.product) {
      return '(Custom Project)'
    }
    return this.product.name
  }

  public get revisionCount() {
    const order = this.order.x as Order
    /* istanbul ignore if */
    if (!this.order) {
      return NaN
    }
    if (!this.product) {
      return order.revisions + order.adjustment_revisions
    }
    if (this.is(this.NEW) || this.is(this.PAYMENT_PENDING)) {
      return this.product.revisions + order.adjustment_revisions
    }
    return order.revisions + order.adjustment_revisions
  }

  public get expectedTurnaround() {
    const order = this.order.x as Order
    /* istanbul ignore if */
    if (!this.order) {
      return NaN
    }
    if (!this.product) {
      return order.expected_turnaround + order.adjustment_expected_turnaround
    }
    if (this.is(this.NEW) || this.is(this.PAYMENT_PENDING)) {
      return this.product.expected_turnaround + order.adjustment_expected_turnaround
    }
    return order.expected_turnaround + order.adjustment_expected_turnaround
  }

  public get deliveryDate() {
    // @ts-ignore
    return (moment() as Moment).businessAdd(Math.ceil(this.expectedTurnaround))
  }

  public get escrow() {
    const order = this.order.x as Order
    /* istanbul ignore if */
    if (!order) {
      return false
    }
    return !order.escrow_disabled
  }

  public get taskWeight() {
    const order = this.order.x as Order
    if ((!this.product || !this.is(this.NEW))) {
      return order.task_weight + order.adjustment_task_weight
    }
    return this.product.task_weight + order.adjustment_task_weight
  }

  public visitSubmission(submission: Submission) {
    this.$router.push({name: 'Submission', params: {submissionId: submission.id + ''}, query: {editing: 'true'}})
  }

  public statusEndpoint(append: string) {
    return () => {
      this.stateChange.endpoint = `${this.url}${append}/`
      this.stateChange.submitThen(this.order.setX)
    }
  }

  public markInviteSent(order: Order) {
    this.inviteSent = true
    this.order.setX(order)
  }

  public get registerLink() {
    const order = this.order.x as Order
    const baseRoute: RawLocation = {name: 'Login', params: {tabName: 'register'}, query: {}}
    /* istanbul ignore if */
    if (!order) {
      return baseRoute
    }
    baseRoute.query!.claim = order.claim_token
    const nextRoute: RawLocation = {
      name: this.$route.name, params: {...this.$route.params}, query: {...this.$route.query},
    }
    if (this.is(this.COMPLETED)) {
      nextRoute.query!.showAdd = 'true'
    }
    baseRoute.query!.next = this.$router.resolve(nextRoute).href
    return baseRoute
  }

  public addToCollection() {
    if (this.isRegistered) {
      this.showAddSubmission = true
      return
    }
    this.$router.push(this.registerLink)
  }

  public get url() {
    return `/api/sales/v1/order/${this.orderId}/`
  }

  public getOutput(user: User|null) {
    if (!user) {
      return null
    }
    const outputs = this.outputs.list.filter((x: SingleController<Submission>) => {
      const submission = x.x as Submission
      return submission.owner.username === user.username
    })
    if (!outputs.length) {
      return null
    }
    return outputs[0]
  }

  public get buyerSubmission() {
    return this.getOutput(this.buyer as User)
  }

  public get sellerSubmission() {
    return this.getOutput(this.seller as User)
  }

  public updateOrder(order: Order) {
    this.order.updateX(order)
    this.showPayment = false
  }

  public addTags() {
    const tags = []
    for (const char of this.characters.list) {
      const character = char.x as LinkedCharacter
      tags.push(...character.character.tags)
    }
    this.addSubmission.fields.tags.update([...new Set(tags)])
  }

  public is(status: number) {
    /* istanbul ignore if */
    if (!this.order.x) {
      return false
    }
    return this.order.x.status === status
  }

  public created() {
    this.characters = this.$getList(
      `order${this.orderId}__characters`, {endpoint: `${this.url}characters/`, paginated: false},
    )
    this.characters.firstRun().then(this.addTags)
    this.order = this.$getSingle(`order${this.orderId}`, {endpoint: this.url})
    this.order.get().catch(this.setError)
    this.comments = this.$getList(
      `order${this.orderId}-comments`, {
        endpoint: `/api/lib/v1/comments/sales.Order/${this.orderId}/`,
        reverse: true,
        grow: true,
        pageSize: 5,
      })
    // Used as wrapper for state change events.
    this.stateChange = this.$getForm(`order${this.orderId}__stateChange`, {endpoint: this.url, fields: {}})
    this.orderEmail = this.$getForm(`order${this.orderId}__email`, {endpoint: `${this.url}invite/`, fields: {}})
    const schema = baseCardSchema(`${this.url}pay/`)
    schema.fields = {
      ...schema.fields,
      card_id: {value: null},
      service: {value: null},
      amount: {value: 0},
    }
    this.paymentForm = this.$getForm(`order${this.orderId}__payment`, schema)
    this.revisions = this.$getList(
      `order${this.orderId}__revisions`, {endpoint: `${this.url}revisions/`, paginated: false}
    )
    this.revisions.firstRun().catch()
    const outputUrl = `${this.url}outputs/`
    this.outputs = this.$getList(`order${this.orderId}__outputs`, {endpoint: outputUrl})
    this.addSubmission = this.$getForm(`order${this.orderId}__addSubmission`, {
      endpoint: outputUrl,
      fields: {
        title: {value: ''},
        caption: {value: ''},
        private: {value: false},
        tags: {value: []},
        comments_disabled: {value: false},
      },
    })
    this.$listenForSingle(`${this.orderId}__rate__buyer`)
    this.$listenForSingle(`${this.orderId}__rate__seller`)
    if (this.$route.query.showAdd) {
      this.showAddSubmission = true
    }
    if (this.$route.query.showConfirm) {
      this.showConfirm = true
    }
  }
}
</script>
