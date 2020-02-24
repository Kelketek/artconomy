<template>
  <ac-load-section :controller="order">
    <template v-slot:default>
      <v-row dense>
        <v-col cols="12" md="3" lg="2" order="4" order-md="1">
          <v-toolbar dense color="black">
            <ac-avatar :user="order.x.seller" :show-name="false" />
            <v-toolbar-title class="ml-1"><ac-link :to="profileLink(order.x.seller)">{{order.x.seller.username}}</ac-link></v-toolbar-title>
          </v-toolbar>
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken2">
            <v-card-text >
              <v-row dense>
                <v-col class="py-2 subheading" cols="12" >
                  {{name}}
                </v-col>
                <v-col cols="6" md="12">
                  <ac-asset :asset="order.x.display" thumb-name="thumbnail" />
                </v-col>
                <v-col cols="6" md="12" align-self="center" class="text-center text-md-left">
                  Placed on: {{formatDateTime(order.x.created_on)}}
                  <div v-if="is(NEW)">
                    <span v-if="revisionCount">
                    <strong>{{revisionCount}}</strong> revision<span v-if="revisionCount > 1">s</span> included.
                    </span><br v-if="revisionCount" />
                    <span>Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong></span><br />
                  </div>
                  <ac-escrow-label :escrow="escrow" name="order" />
                </v-col>
                <v-col cols="12" class="pt-2">
                  <v-row no-gutters>
                    <v-col v-if="isStaff">
                      <v-select
                          v-model="viewMode"
                          :items="viewerItems"
                          label="View as..."
                          outline
                          class="view-mode-select"
                      />
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="6" lg="7" order="1" order-md="2">
          <v-row dense>
            <v-col cols="12">
              <v-toolbar dense v-if="buyer" color="black">
                <ac-avatar :username="buyer.username" :show-name="false" />
                <v-toolbar-title class="ml-1"><ac-link :to="profileLink(buyer)">{{deriveDisplayName(buyer.username)}}</ac-link></v-toolbar-title>
              </v-toolbar>
              <v-card>
                <v-card-text>
                  <v-row dense>
                    <v-col align-self="center">
                      <h2><span v-if="isSeller">Sale</span>
                      <span v-else-if="isArbitrator">Case</span>
                      <span v-else>Order</span>
                      #{{order.x.id}}
                      Details:</h2>
                    </v-col>
                    <v-col class="text-right" align-self="center">
                      <v-chip color="white" light v-if="order.x.private" class="ma-1">
                        <v-icon left>visibility_off</v-icon>
                        Private
                      </v-chip>
                      <ac-order-status :order="order.x" class="ma-1" />
                      <v-btn class="ma-1 rating-button pa-1" small :color="ratingColor[order.x.rating]" :ripple="false">
                        {{ratingsShort[order.x.rating]}}
                      </v-btn>
                    </v-col>
                  </v-row>
                  <ac-rendered :value="order.x.details" />
                  <v-col v-if="isSeller && (!buyer || buyer.guest) && !(is(COMPLETED) || is(DISPUTED) || is(REFUNDED) || is(CANCELLED))" cols="12">
                    <ac-form @submit.prevent="orderEmail.submitThen(markInviteSent)">
                    <ac-form-container v-bind="orderEmail.bind">
                      <v-row dense class="justify-content"  align-content="center">
                        <v-col>
                          <ac-patch-field
                            label="Customer email address"
                            hint="Set and save this to send the customer an invite link."
                            :persistent-hint="true"
                            :patcher="order.patchers.customer_email"
                            :refresh="false"
                          />
                        </v-col>
                        <v-col class="shrink d-flex" align-self="center">
                          <v-btn
                            :disabled="inviteDisabled"
                            color="primary"
                            type="submit"
                            class="send-invite-button"
                          >Send Invite Link</v-btn>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col cols="12">
                          <v-alert v-model="inviteSent" :dismissible="true" type="success">
                            Invite email sent!
                          </v-alert>
                        </v-col>
                      </v-row>
                    </ac-form-container>
                    </ac-form>
                  </v-col>
                  <v-subheader v-if="commissionInfo">Commission Info</v-subheader>
                  <ac-rendered :value="commissionInfo" :truncate="200" />
                  <ac-price-preview
                    :price="order.x.price"
                    :line-items="lineItems"
                    :username="order.x.seller.username"
                    :is-seller="isSeller"
                    :editable="(is(NEW) || is(PAYMENT_PENDING)) && (isSeller || isArbitrator)"
                    :editBase="!product"
                    :escrow="!order.x.escrow_disabled"
                  />
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
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" v-if="characters.list.length">
              <v-card-text>
                <ac-load-section :controller="characters">
                  <template v-slot:default>
                    <ac-character-display :controller="characters" :editable="false" />
                  </template>
                </ac-load-section>
              </v-card-text>
            </v-col>
            <v-col cols="12">
              <ac-revision-manager
                  :list="revisions" :is-seller="isSeller || isArbitrator"
                  :order="order"
                  :hidden="order.x.revisions_hidden"
                  :archived="(is(COMPLETED) || is(REFUNDED) || is(CANCELLED)) && !order.x.escrow_disabled"
                  @finalize="statusEndpoint('complete')()"
                  @reopen="statusEndpoint('reopen')()"
                  :revision-count="revisionCount"
              />
            </v-col>
            <v-col class="text-center" cols="12" v-if="isBuyer && is(REVIEW)" >
              <v-btn color="primary" @click="statusEndpoint('approve')()">Approve Final</v-btn>
              <v-btn color="danger" @click="statusEndpoint('dispute')()">File Dispute</v-btn>
            </v-col>
            <v-col class="text-center" cols="12" v-if="isBuyer && is(DISPUTED)" >
              <p><strong>Your dispute has been filed.</strong> Please stand by for further instructions.
                If you are able to work out your disagreement with the artist, please approve the order using the
                button below.</p>
              <ac-confirmation :action="statusEndpoint('approve')">
                <template v-slot:default="{on}">
                  <v-btn color="primary" v-on="on">Approve Final</v-btn>
                </template>
              </ac-confirmation>
            </v-col>
            <v-col class="d-flex" cols="12" sm="6" md="8" v-if="isBuyer && (is(COMPLETED) || is(REFUNDED))" >
              <ac-order-rating end="seller" :order-id="orderId" key="seller" />
            </v-col>
            <v-col cols="12" v-if="buyer && isSeller && (is(COMPLETED) || is(REFUNDED))">
              <ac-order-rating end="buyer" :order-id="orderId" key="buyer" />
            </v-col>
            <v-col class="text-center pt-2" v-if="isBuyer && is(COMPLETED)" cols="12" sm="6" md="4" >
              <v-img src="/static/images/fridge.png" max-height="20vh" contain />
              <v-btn v-if="buyerSubmission" color="primary"
                     :to="{name: 'Submission', params: {submissionId: buyerSubmission.x.id}}">Visit in Collection</v-btn>
              <v-btn color="green" v-else @click="addToCollection" class="collection-add">Add to Collection</v-btn>
            </v-col>
            <v-col cols="12" v-if="$vuetify.breakpoint.mdAndUp">
              <ac-comment-section :commentList="comments" :nesting="false" :locked="!isInvolved" :guest-ok="true" :show-history="isArbitrator" />
            </v-col>
          </v-row>
        </v-col>
        <v-col class="pa-1" cols="12" md="3" lg="3" order="2" order-md="3">
          <v-card>
            <v-card-title><h3>Now what?</h3></v-card-title>
            <ac-form>
            <ac-form-container @submit.prevent="stateChanger" :errors="stateChange.errors" :sending="stateChange.sending">
            <v-card-text>
              <v-row dense>
                <v-col v-if="is(NEW) && isBuyer" cols="12">
                  <p>Your order has been placed and is awaiting the artist's review. You will receive an email when the
                    artist has accepted or rejected the order, or if they have any comments.</p>
                  <p>You may add additional comments or questions below!</p>
                </v-col>
                <v-col v-if="is(NEW) && isSeller" cols="12">
                  <p>This order is pending your review. Please make any pricing adjustments and accept the order, or
                    reject the order if you are unwilling or unable to complete the piece.</p>
                  <p>You may add comments to ask the commissioner questions.</p>
                </v-col>
                <v-col class="text-center" v-if="!is(COMPLETED) && !isRegistered" cols="12" >
                  <v-btn color="green" :to="registerLink" class="link-account">Link an Account</v-btn>
                </v-col>
                <v-col class="pb-2" v-if="(is(NEW) && isSeller) || !(is(NEW) || is(CANCELLED))" cols="12" >
                  <v-divider />
                  Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong><br />
                  <span v-if="revisionCount">Revisions: <strong>{{revisionCount}}</strong></span><br v-if="revisionCount" />
                  <span v-if="isSeller">AWOO Task Weight: <strong>{{taskWeight}}</strong></span>
                </v-col>
                <v-col cols="12" v-if="(is(NEW) || is(PAYMENT_PENDING)) && isSeller">
                  <v-row no-gutters  >
                    <v-col cols="12">
                      <ac-patch-field
                          :patcher="order.patchers.adjustment"
                          field-type="ac-price-field"
                          label="Surcharges/Discounts (USD)"
                      />
                    </v-col>
                    <v-col cols="12">
                      <ac-patch-field
                          :patcher="order.patchers.adjustment_expected_turnaround"
                          label="Additional Days Required"
                      />
                    </v-col>
                    <v-col cols="12">
                      <ac-patch-field
                        :patcher="order.patchers.adjustment_revisions"
                        label="Additional Revisions Offered"
                      />
                    </v-col>
                    <v-col cols="12">
                      <ac-patch-field
                          :patcher="order.patchers.adjustment_task_weight"
                          label="Additional task weight"
                      />
                    </v-col>
                    <v-col class="text-center" cols="12" >
                      <ac-confirmation :action="statusEndpoint('accept')" v-if="is(NEW)">
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
                  </v-row>
                </v-col>
                <ac-escrow-label :escrow="!order.x.escrow_disabled" v-if="is(PAYMENT_PENDING) && isBuyer" name="order" />
                <v-col v-if="is(PAYMENT_PENDING) && isBuyer" cols="12">
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
                </v-col>
                <v-col class="text-center payment-section" v-if="is(PAYMENT_PENDING) && isBuyer && !order.x.escrow_disabled" cols="12" >
                  <v-btn color="green" @click="showPayment = true" class="payment-button">Send Payment</v-btn>
                  <ac-form-dialog v-model="showPayment" @submit.prevent="paymentForm.submitThen(updateOrder)" :large="true" v-bind="paymentForm.bind">
                    <v-row>
                      <v-col class="text-center" cols="12" >Total Charge: <strong>${{totalCharge.toFixed(2)}}</strong></v-col>
                      <v-col cols="12">
                        <ac-card-manager
                            ref="cardManager"
                            :payment="true"
                            :username="buyer.username"
                            :cc-form="paymentForm"
                            :field-mode="true"
                            v-model="paymentForm.fields.card_id.model"
                        />
                      </v-col>
                      <v-col cols="12" v-if="seller.landscape && !order.x.escrow_disabled" class="text-xs-center">
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
                          :price="order.x.price"
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
                <v-col v-if="isBuyer && order.x.stream_link && !(is(COMPLETED) || is(CANCELLED) || is(REFUNDED))" cols="12">
                  <p><a :href="order.x.stream_link" target="_blank">Your artist is streaming your commission here!</a></p>
                </v-col>
                <v-col v-if="is(PAYMENT_PENDING) && isSeller" cols="12">
                  <p>The commissioner has been informed that they must now pay in order for you to work on the order.
                    You may continue to comment and tweak pricing in the interim, or you may cancel the order if you need to.</p>
                  <p v-if="order.x.escrow_disabled">
                    <strong>REMEMBER:</strong> As we are not handling payment for this order, you MUST tell your
                    commissioner how to pay you. Leave a comment telling them how if you have not done so already.
                    When the customer has paid, click the 'Mark Paid' button.</p>
                  <p v-else>
                    You may mark this order as paid, if the customer has paid you through an outside method, or you wish to waive payment for this commission.
                  </p>
                  <v-col class="text-center" v-if="order.x.escrow_disabled">
                    <v-btn color="primary" @click="statusEndpoint('mark-paid')()">Mark Paid</v-btn>
                  </v-col>
                  <ac-confirmation :action="statusEndpoint('mark-paid')" v-else>
                    <template v-slot:default="{on}">
                      <v-col class="text-center" cols="12">
                        <v-btn color="primary" v-on="on">Mark Paid</v-btn>
                      </v-col>
                    </template>
                    <v-col slot="confirmation-text">
                      <p>Artconomy will not be able to protect you from fraud if your customer has paid through an outside
                        method.</p>
                      <p><strong>Don't do this unless you really know what you're doing!</strong></p>
                        <p>If you are having trouble, please contact support.</p>
                    </v-col>
                  </ac-confirmation>
                </v-col>
                <v-col v-if="isSeller && is(REVIEW)" cols="12">
                  <p>The commissioner has been informed that the final is ready for their review. Please stand by for final approval!</p>
                </v-col>
                <v-col v-if="is(REVIEW)" cols="12">
                  <p>This order will auto-finalize on <strong>{{formatDateTerse(order.x.auto_finalize_on)}}</strong>.</p>
                </v-col>
                <v-col v-if="isBuyer && is(REVIEW)" cols="12">
                  <p>Your artist has completed the piece! If all is well, please hit approve. Otherwise, if there is an
                    issue you cannot resolve with the artist, please hit the dispute button.</p>
                  <v-col class="text-center" >
                    <v-btn color="primary" @click="statusEndpoint('approve')()">Approve Final</v-btn>
                    <v-btn color="danger" @click="statusEndpoint('dispute')()">File Dispute</v-btn>
                  </v-col>
                </v-col>
                <v-col class="text-center pt-2" cols="12" v-if="isBuyer && is(DISPUTED)" >
                  <p><strong>Your dispute has been filed.</strong> Please stand by for further instructions.
                    If you are able to work out your disagreement with the artist, please approve the order using the
                    button below.</p>
                </v-col>
                <v-col class="text-center" v-if="(isBuyer || isArbitrator) && is(DISPUTED)" cols="12" >
                  <ac-confirmation :action="statusEndpoint('approve')">
                    <template v-slot:default="{on}">
                      <v-btn color="primary" v-on="on">Approve Final</v-btn>
                    </template>
                  </ac-confirmation>
                </v-col>
                <v-col class="text-center" v-if="is(NEW) || is(PAYMENT_PENDING)" cols="12">
                  <ac-confirmation :action="statusEndpoint('cancel')">
                    <template v-slot:default="{on}">
                      <v-btn v-on="on">Cancel</v-btn>
                    </template>
                  </ac-confirmation>
                </v-col>
                <v-col v-if="is(QUEUED) && isBuyer" cols="12">
                  <p>Your order has been added to the artists queue. We will notify you when they have begun work!</p>
                </v-col>
                <v-col v-if="is(QUEUED) && isSeller" cols="12">
                  <p><strong>Excellent!</strong> The commissioner has paid<span v-if="escrow"> and the money is being held in safekeeping</span>.
                    When you've started work, hit the 'Mark In Progress' button to let the customer know.
                    You can also set the order's streaming link (if applicable) here:</p>
                </v-col>
                <v-col v-if="order.x.dispute_available_on && !(is(DISPUTED) || is(REVIEW) || is(COMPLETED) || is(REFUNDED))" cols="12">
                  <p v-if="disputeTimeElapsed">You may file dispute for non-completion if needed.</p>
                  <p v-else>This order may be disputed for non-completion on: <br /><strong>{{formatDateTerse(order.x.dispute_available_on)}}.</strong></p>
                  <v-col class="text-center" >
                  <v-btn v-if="disputeTimeElapsed && isBuyer" @click="statusEndpoint('dispute')()" color="danger">File Dispute</v-btn>
                  </v-col>
                </v-col>
                <v-col v-if="isSeller && (is(QUEUED) || is(IN_PROGRESS) || is(REVIEW) || is(DISPUTED))" cols="12">
                  <v-alert :value="order.x.private">
                    <strong>NOTE:</strong> This user has asked that this commission be private. Please do not use a public streaming link!
                  </v-alert>
                  <ac-patch-field
                      :patcher="order.patchers.stream_link" label="Stream URL">
                  </ac-patch-field>
                </v-col>
                <v-col v-if="isBuyer && is(IN_PROGRESS)">
                  <p>The artist has begun work on your order. You'll be notified as they make progress!</p>
                </v-col>
                <v-col class="text-center" v-if="is(QUEUED) && isSeller" cols="12">
                  <v-btn color="primary" @click="statusEndpoint('start')()">Mark In Progress</v-btn>
                </v-col>
                <v-col v-if="is(DISPUTED) && isSeller">
                  <p><strong>This order is under dispute.</strong> One of our staff will be along soon to give further
                    instruction. If you wish, you may refund the customer. Otherwise, please wait for our staff to work
                    with you and the commissioner on a resolution.</p>
                </v-col>
                <v-col class="text-center" v-if="is(COMPLETED)" cols="12" >
                  <p>This order has been completed! <strong>Thank you for using Artconomy!</strong></p>
                </v-col>
                <v-col class="text-center" v-if="is(COMPLETED) && disputeWindow && isBuyer" cols="12">
                  <v-alert :value="true" type="info">If there is an issue with this order, please <a href="#" @click.prevent="setSupport(true)">contact support</a>
                    on or before {{formatDateTerse(order.x.auto_finalize_on)}}.</v-alert>
                </v-col>
                <v-col class="text-center" v-if="is(REFUNDED)" cols="12" >
                  <p>This order has been refunded and is now archived.</p>
                </v-col>
                <v-col class="text-center" v-if="isSeller && escrow && is(COMPLETED)" cols="12" >
                  <p><router-link :to="{name: 'Payout', params: {username: seller.username}}">
                    If you have not already, please add your bank account in your payout settings.</router-link></p>
                  <p>A transfer will automatically be initiated to your bank account.
                    Please wait up to five business days for payment to post.</p>
                </v-col>
                <v-col class="text-center" v-if="isSeller && is(COMPLETED) && !order.x.private" cols="12" >
                  <v-img src="/static/images/fridge.png" max-height="20vh" contain />
                  <v-btn v-if="sellerSubmission" color="primary"
                         :to="{name: 'Submission', params: {submissionId: sellerSubmission.x.id}}">Visit in Gallery</v-btn>
                  <v-btn color="green" v-else @click="showAddSubmission = true">Add to my Gallery</v-btn>
                </v-col>
                <v-col class="text-center" v-if="isBuyer && is(COMPLETED)" cols="12" >
                  <v-btn v-if="buyerSubmission" color="primary"
                         :to="{name: 'Submission', params: {submissionId: buyerSubmission.x.id}}">Visit in Collection</v-btn>
                  <v-btn color="green" v-else @click="addToCollection" class="collection-add">Add to Collection</v-btn>
                </v-col>
                <v-col v-if="is(CANCELLED) && isBuyer">
                  <p>This order has been cancelled. You will have to create a new order if you want a commission.</p>
                </v-col>
                <v-col v-if="is(CANCELLED) && isSeller">
                  <p>This order has been cancelled. There is nothing more to do.</p>
                </v-col>
                <ac-form-dialog
                    v-if="is(COMPLETED)"
                    @submit.prevent="addSubmission.submitThen(visitSubmission)"
                    v-model="showAddSubmission"
                    :sending="addSubmission.sending"
                    :errors="addSubmission.errors"
                    v-bind="addSubmission.bind"
                    :large="true"
                    :eager="true"
                    :title="isSeller ? 'Add to Gallery' : 'Add to Collection'"
                >
                  <v-container class="pa-0">
                    <v-row no-gutters  >
                      <v-col cols="12">
                        <ac-bound-field :field="addSubmission.fields.title" label="Title" />
                      </v-col>
                      <v-col cols="12">
                        <ac-bound-field
                            :field="addSubmission.fields.caption"
                            field-type="ac-editor" :save-indicator="false"
                            label="Caption"
                            hint="Tell viewers a little about the piece."
                            :persistent-hint="true"
                        />
                      </v-col>
                      <v-col cols="12">
                        <ac-bound-field
                            :field="addSubmission.fields.tags" field-type="ac-tag-field" label="Tags"
                            hint="Add some tags to make this submission easier to manage. We've added all the tags of
                            the characters attached to this piece (if any) to help!"
                            :persistent-hint="true"
                        />
                      </v-col>
                      <v-col cols="12" sm="6">
                        <ac-bound-field :field="addSubmission.fields.private" label="Private" field-type="v-checkbox"
                                        hint="If checked, will not show this submission to anyone you've not explicitly shared it with."
                        />
                      </v-col>
                      <v-col cols="12" sm="6">
                        <ac-bound-field :field="addSubmission.fields.comments_disabled" label="Comments Disabled" field-type="v-checkbox"
                                        hint="If checked, prevents others from commenting on this submission."
                        />
                      </v-col>
                    </v-row>
                  </v-container>
                </ac-form-dialog>
              </v-row>
            </v-card-text>
            </ac-form-container>
            </ac-form>
          </v-card>
        </v-col>
        <ac-expanded-property v-model="showConfirm">
          <span slot="title">We're on it!</span>
          <v-row align="center" class="order-confirmation justify-content-center">
            <v-col cols="12" sm="6" md="3" align-self="center">
              <v-img src="/static/images/cheering.png" :contain="true" max-height="30vh" />
            </v-col>
            <v-col cols="12" sm="6" md="9" align-self="center">
              <h1 class="display-1">Order Placed.</h1>
              <h2 class="headline">Check your email!</h2>
              <p>We've sent a confirmation to your email address. If you haven't received it, please check your spam folder.</p>
              <p>
                <strong>It is very important that you verify you're getting emails from Artconomy, or else your artist
                  won't be able to send you messages on their progress.</strong> If you're having trouble,
                <a href="#" @click.prevent="setSupport(true)">please contact support</a> or ask for help in the <a href="https://t.me/Artconomy" target="_blank">Artconomy Telegram group</a>.</p>
              <p>Your artist will contact you soon to confirm acceptance of your commission, or ask additional questions.</p>
            </v-col>
          </v-row>
        </ac-expanded-property>
        <v-col cols="12" v-if="$vuetify.breakpoint.smAndDown" order="3">
          <ac-comment-section :commentList="comments" :nesting="false" :locked="!isInvolved" :guest-ok="true" :show-history="isArbitrator" />
        </v-col>
      </v-row>
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
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {baseCardSchema} from '@/lib/lib'
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
import LineItem from '@/types/LineItem'
import {getTotals, quantize, totalForTypes} from '@/lib/lineItemFunctions'
import {LineTypes} from '@/types/LineTypes'
import LineAccumulator from '@/types/LineAccumulator'
import Big from 'big.js'

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
  public lineItems: ListController<LineItem> = null as unknown as ListController<LineItem>
  public revisions: ListController<Revision> = null as unknown as ListController<Revision>
  public outputs: ListController<Submission> = null as unknown as ListController<Submission>
  public stateChange: FormController = null as unknown as FormController
  public paymentForm: FormController = null as unknown as FormController
  public tipForm: FormController = null as unknown as FormController
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

  @Watch('totalCharge')
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
    if (!this.lineItems) {
      return {total: Big(0), map: new Map()}
    }
    return getTotals(this.bareLines)
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

  public get disputeWindow() {
    /* istanbul ignore if */
    if (!this.order.x) {
      return false
    }
    if (!this.order.x.trust_finalized) {
      return false
    }
    // @ts-ignore
    return (moment(this.order.x.auto_finalize_on) as Moment) >= (moment() as Moment)
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
    // @ts-ignore
    window.stuff = this
    this.characters = this.$getList(
      `order${this.orderId}__characters`, {endpoint: `${this.url}characters/`, paginated: false},
    )
    this.characters.firstRun().then(this.addTags)
    this.order = this.$getSingle(`order${this.orderId}`, {endpoint: this.url})
    this.order.get().catch(this.setError)
    this.lineItems = this.$getList(`order${this.orderId}__lineItems`, {
      endpoint: `${this.url}line-items/`,
      paginated: false,
    })
    this.lineItems.firstRun()
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
    this.tipForm = this.$getForm(`order${this.orderId}__tip`, {
      endpoint: `${this.url}line-items/`,
      fields: {
        amount: {value: 0, validators: [{name: 'numeric'}]},
        percentage: {value: 0},
        type: {value: LineTypes.TIP},
      },
    })
    this.revisions = this.$getList(
      `order${this.orderId}__revisions`, {endpoint: `${this.url}revisions/`, paginated: false}
    )
    this.revisions.firstRun().catch(() => {})
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
