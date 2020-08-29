<template>
  <ac-load-section :controller="deliverable">
    <template v-slot:default>
      <v-container>
        <v-row>
          <v-col>
            <v-card>
              <v-card-title><h3>Now what?</h3></v-card-title>
              <ac-form>
                <ac-form-container @submit.prevent="stateChange.submitThen(updateDeliverable)" :errors="stateChange.errors" :sending="stateChange.sending">
                  <v-card-text>
                    <v-row dense>
                      <v-col v-if="is(WAITING) && isBuyer" cols="12">
                        <p>Your order has been placed in the artist's waitlist. Waitlisted orders are not guaranteed by
                          Artconomy to be accepted in any order and every artist's policy is different in how they are handled.
                          If your artist has not listed their waitlist policy for this commission in the product details,
                          or in their commission info under the Overview tab, you may want to message them for clarification.</p>
                      </v-col>
                      <v-col v-if="is(WAITING) && isSeller" cols="12">
                        <p>This order is in your waitlist. You should put your waitlist policy in your commission info in your
                          <router-link :to="{name: 'Artist', params: {username: seller.username}}">Artist Settings</router-link>
                          if you have not already, or else add it to the details of the product this order is associated with.
                        </p>
                      </v-col>
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
                      <v-col v-if="is(PAYMENT_PENDING) && isBuyer" cols="12">
                        <v-divider />
                        <p>
                          <strong>Congratulations!</strong> Your artist has accepted your order. Please submit payment so that it can be added to their work queue.
                          <span v-if="deliverable.x.escrow_disabled">Your artist will inform you on how to pay them.</span>
                        </p>
                        <p v-if="!deliverable.x.escrow_disabled">
                          <strong class="danger">WARNING:</strong> Only send payment using the <strong>'Send Payment'</strong> button in the '<strong>Payment</strong>' <span v-if="$vuetify.breakpoint.mdAndUp">tab</span><span v-else>dropdown option</span> directly below this section.
                          Do not use any other method, button, or link, or we will not be able to protect you from fraud. If your
                          artist asks for payment using another method, or if you are getting errors, please <a @click="setSupport(true)">contact support.</a>
                        </p>
                      </v-col>
                      <v-col v-if="isBuyer && deliverable.x.stream_link && !(is(COMPLETED) || is(CANCELLED) || is(REFUNDED))" cols="12">
                        <p><a :href="deliverable.x.stream_link" target="_blank">Your artist is streaming your commission here!</a></p>
                      </v-col>
                      <v-col v-if="is(PAYMENT_PENDING) && isSeller" cols="12">
                        <p>The commissioner has been informed that they must now pay in order for you to work on the order.
                          You may continue to comment and tweak pricing in the interim, or you may cancel the order if you need to.</p>
                        <p v-if="deliverable.x.escrow_disabled">
                          <strong>REMEMBER:</strong> As we are not handling payment for this order, you MUST tell your
                          commissioner how to pay you. Leave a comment telling them how if you have not done so already.
                          When the customer has paid, click the 'Mark Paid' button.</p>
                        <p v-else>
                          You may mark this order as paid, if the customer has paid you through an outside method, or you wish to waive payment for this commission.
                        </p>
                        <v-col class="text-center" v-if="deliverable.x.escrow_disabled">
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
                        <p>This order will auto-finalize on <strong>{{formatDateTerse(deliverable.x.auto_finalize_on)}}</strong>.</p>
                      </v-col>
                      <template v-if="isBuyer && is(REVIEW)">
                        <v-col cols="12">
                          <p>Your artist has completed the piece! If all is well, please hit approve. Otherwise, if there is an
                            issue you cannot resolve with the artist, please hit the dispute button.</p>
                        </v-col>
                        <v-row>
                          <v-col class="text-center">
                            <v-btn color="primary" @click="statusEndpoint('approve')()">Approve Final</v-btn>
                          </v-col>
                          <v-col class="text-center">
                            <v-btn color="danger" @click="statusEndpoint('dispute')()">File Dispute</v-btn>
                          </v-col>
                        </v-row>
                      </template>
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
                      <v-row v-if="is(WAITING) || is(NEW) || is(PAYMENT_PENDING)">
                        <v-col class="text-center">
                          <ac-confirmation :action="statusEndpoint('cancel')">
                            <template v-slot:default="{on}">
                              <v-btn v-on="on">Cancel Order</v-btn>
                            </template>
                          </ac-confirmation>
                        </v-col>
                        <v-col class="text-center">
                          <v-btn
                            color="primary" v-if="$route.params.deliverableId"
                            :to="{name: `${baseName}DeliverablePayment`,
                            params: {...$route.params}}"
                            @click="scrollToSection"
                            class="review-terms-button"
                          >Review Terms/Pricing<span v-if="is(PAYMENT_PENDING) && isBuyer">/Pay</span></v-btn>
                        </v-col>
                        <v-col v-if="isBuyer" class="text-center">
                          <v-btn color="secondary" v-if="$route.params.deliverableId" :to="{name: `${baseName}DeliverableReferences`, params: {...$route.params}}">Add References</v-btn>
                        </v-col>
                      </v-row>
                      <v-col v-if="is(QUEUED) && isBuyer" cols="12">
                        <p>Your order has been added to the artists queue. We will notify you when they have begun work!</p>
                      </v-col>
                      <v-col v-if="is(QUEUED) && isSeller" cols="12">
                        <p><strong>Excellent!</strong> The commissioner has paid<span v-if="escrow"> and the money is being held in safekeeping</span>.
                          When you've started work, hit the 'Mark In Progress' button to let the customer know.
                          You can also set the order's streaming link (if applicable) here:</p>
                      </v-col>
                      <v-col v-if="deliverable.x.dispute_available_on && !(is(DISPUTED) || is(REVIEW) || is(COMPLETED) || is(REFUNDED))" cols="12">
                        <p v-if="disputeTimeElapsed">You may file dispute for non-completion if needed.</p>
                        <p v-else>This order may be disputed for non-completion on: <br /><strong>{{formatDateTerse(deliverable.x.dispute_available_on)}}.</strong></p>
                        <v-col class="text-center" >
                          <v-btn v-if="disputeTimeElapsed && isBuyer" @click="statusEndpoint('dispute')()" color="danger">File Dispute</v-btn>
                        </v-col>
                      </v-col>
                      <v-col v-if="isSeller && (is(QUEUED) || is(IN_PROGRESS) || is(REVIEW) || is(DISPUTED))" cols="12">
                        <v-alert :value="order.x.private">
                          <strong>NOTE:</strong> This user has asked that this commission be private. Please do not use a public streaming link!
                        </v-alert>
                        <ac-patch-field
                          :patcher="deliverable.patchers.stream_link" label="Stream URL">
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
                          on or before {{formatDateTerse(deliverable.x.auto_finalize_on)}}.</v-alert>
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
                        <v-btn color="green" v-else @click="viewSettings.patchers.showAddSubmission.model = true">Add to my Gallery</v-btn>
                      </v-col>
                      <v-col class="text-center" v-if="isBuyer && is(COMPLETED)" cols="12" >
                        <v-img src="/static/images/fridge.png" max-height="20vh" contain />
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
                        v-model="viewSettings.patchers.showAddSubmission.model"
                        :sending="addSubmission.sending"
                        :errors="addSubmission.errors"
                        v-bind="addSubmission.bind"
                        :large="true"
                        :eager="true"
                        class="add-submission-dialog"
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
                              <ac-bound-field :field="addSubmission.fields.private" label="Private" field-type="ac-checkbox"
                                              hint="If checked, will not show this submission to anyone you've not explicitly shared it with."
                              />
                            </v-col>
                            <v-col cols="12" sm="6">
                              <ac-bound-field :field="addSubmission.fields.comments_disabled" label="Comments Disabled" field-type="ac-checkbox"
                                              hint="If checked, prevents others from commenting on this submission."
                              />
                            </v-col>
                          </v-row>
                        </v-container>
                      </ac-form-dialog>
                      <ac-form-dialog
                        v-if="isSeller && seller"
                        @submit.prevent="newInvoice.submitThen(visitDeliverable)"
                        v-model="viewSettings.patchers.showAddDeliverable.model"
                        v-bind="newInvoice.bind"
                        :large="true"
                        :eager="true"
                        :title="'Add new Deliverable to Order.'"
                      >
                        <v-container class="pa-0">
                          <ac-invoice-form :new-invoice="newInvoice" :username="seller.username" :line-items="invoiceLineItems" :escrow-disabled="invoiceEscrowDisabled" :show-buyer="false">
                            <template v-slot:second>
                              <v-col cols="12" sm="6">
                                <v-row no-gutters>
                                  <v-col cols="12" sm="6" md="4" offset-sm="3" offset-md="4">
                                    <ac-bound-field
                                      :field="newInvoice.fields.name"
                                      label="Deliverable Name"
                                      hint="Give this deliverable a name, like 'Page 2' or 'Inks'. This will help distinguish it from the other deliverables in the order."
                                    />
                                  </v-col>
                                </v-row>
                              </v-col>
                              <v-col cols="12" sm="6">
                                <v-checkbox v-model="keepReferences"
                                            label="Keep References"
                                            hint="Carries the references from the current deliverable over to the next one."
                                            :persistent-hint="true"
                                />
                              </v-col>
                              <v-col cols="12" sm="6">
                                <ac-bound-field :field="newInvoice.fields.characters"
                                                :init-items="viewSettings.patchers.characterInitItems.model"
                                                field-type="ac-character-select" label="Characters"
                                                hint="Tag the character(s) to be referenced in this deliverable. If they're not listed on Artconomy, you can skip this step." />
                              </v-col>
                            </template>
                          </ac-invoice-form>
                        </v-container>
                      </ac-form-dialog>
                    </v-row>
                  </v-card-text>
                </ac-form-container>
              </ac-form>
            </v-card>
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
        <ac-tab-nav :items="navItems"></ac-tab-nav>
        <div class="section-scroll-target"></div>
        <router-view></router-view>
      </v-container>
    </template>
  </ac-load-section>
</template>
<script lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Component, {mixins} from 'vue-class-component'
import Order from '@/types/Order'
import {Watch} from 'vue-property-decorator'
import AcProductPreview from '@/components/AcProductPreview.vue'
import AcAsset from '@/components/AcAsset.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'
import AcRendered from '@/components/wrappers/AcRendered'
import AcAvatar from '@/components/AcAvatar.vue'
import moment from 'moment-business-days'
import AcCharacterDisplay from '@/components/views/submission/AcCharacterDisplay.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import Ratings from '@/mixins/ratings'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import Submission from '@/types/Submission'
import AcBoundField from '@/components/fields/AcBoundField'
import AcDeliverableRating from '@/components/views/order/AcDeliverableRating.vue'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
import {Location} from 'vue-router'
import AcDeliverableStatus from '@/components/AcDeliverableStatus.vue'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import Deliverable from '@/types/Deliverable'
import DeliverableMixin from './mixins/DeliverableMixin'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import {VIEWER_TYPE} from '@/types/VIEWER_TYPE'
import LinkedCharacter from '@/types/LinkedCharacter'
import {Character} from '@/store/characters/types/Character'
import AcInvoiceForm from '@/components/views/orders/AcInvoiceForm.vue'
import {SingleController} from '@/store/singles/controller'
import LinkedReference from '@/types/LinkedReference'
import InvoicingMixin from '@/components/views/order/mixins/InvoicingMixin'
import {ListController} from '@/store/lists/controller'
import {markRead} from '@/lib/lib'

@Component({
  components: {
    AcInvoiceForm,
    AcTabNav,
    AcForm,
    AcExpandedProperty,
    AcDeliverableStatus,
    AcEscrowLabel,
    AcDeliverableRating,
    AcBoundField,
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
    AcLoadSection,
  },
})
export default class DeliverableDetail extends mixins(DeliverableMixin, Formatting, Ratings, InvoicingMixin) {
  public parentDeliverables: ListController<Deliverable> = null as unknown as ListController<Deliverable>
  // We only place this on DeliverableDetail so it doesn't get run multiple times. All subcomponents are reliant on it,
  // however, so keep this in mind during tests.
  @Watch('deliverable.x.id')
  public prePopulate() {
    const deliverable = this.deliverable.x as Deliverable
    const order = deliverable.order as Order
    if (deliverable.arbitrator) {
      this.arbitratorHandler = this.$getProfile(deliverable.arbitrator.username, {})
      this.ensureHandler(this.arbitratorHandler, deliverable.arbitrator)
    }
    this.outputs.setList(deliverable.outputs)
    this.outputs.fetching = false
    this.outputs.ready = true
    this.addSubmission.fields.private.update(order.private)
    this.newInvoice.fields.details.update(deliverable.details)
    this.newInvoice.fields.rating.update(deliverable.rating)
    this.order.setX(order)
    this.order.ready = true
  }

  @Watch('references.list.length')
  public updateReferences(val: number|undefined) {
    /* istanbul ignore if */
    if (val === undefined) {
      return
    }
    this.setReferences()
  }

  public get viewerItems() {
    const items = [{text: 'Staff', value: VIEWER_TYPE.STAFF}]
    if (this.buyer) {
      items.push({text: 'Buyer', value: VIEWER_TYPE.BUYER})
    }
    items.push({text: 'Seller', value: VIEWER_TYPE.SELLER})
    return items
  }

  public get disputeTimeElapsed() {
    const deliverable = this.deliverable.x as Deliverable
    /* istanbul ignore if */
    if (!deliverable) {
      return false
    }
    if (!deliverable.dispute_available_on) {
      return false
    }
    // @ts-ignore
    return moment(deliverable.dispute_available_on) < moment.now()
  }

  public visitSubmission(submission: Submission) {
    this.$router.push({name: 'Submission', params: {submissionId: submission.id + ''}, query: {editing: 'true'}})
  }

  public get sellerName() {
    if (this.seller) {
      return this.seller.username
    }
    return ''
  }

  public get registerLink() {
    const order = this.order.x as Order
    const baseRoute: Location = {name: 'Login', params: {tabName: 'register'}, query: {}}
    /* istanbul ignore if */
    if (!order) {
      return baseRoute
    }
    baseRoute.query!.claim = order.claim_token
    /* istanbul ignore next */
    const nextRoute: Location = {
      name: this.$route.name || undefined, params: {...this.$route.params}, query: {...this.$route.query},
    }
    if (this.is(this.COMPLETED)) {
      nextRoute.query!.showAdd = 'true'
    }
    baseRoute.query!.next = this.$router.resolve(nextRoute).href
    return baseRoute
  }

  public get navItems() {
    const params = {...this.$route.params}
    if (!params.deliverableId) {
      // We're transitioning to another area. Return no items.
      return []
    }
    return [
      {
        value: {name: `${this.baseName}DeliverableOverview`, params}, text: 'Overview',
      },
      {
        value: {name: `${this.baseName}DeliverableReferences`, params}, text: 'References/Characters',
      },
      {
        value: {name: `${this.baseName}DeliverablePayment`, params}, text: 'Payment/Terms',
      },
      {
        value: {name: `${this.baseName}DeliverableRevisions`, params}, text: 'Revisions',
      },
    ]
  }

  public addToCollection() {
    if (this.isRegistered) {
      this.viewSettings.model.showAddSubmission = true
      return
    }
    this.$router.push(this.registerLink)
  }

  public scrollToSection() {
    this.$vuetify.goTo('.section-scroll-target')
  }

  public visitDeliverable(deliverable: Deliverable) {
    this.order.updateX({deliverable_count: (this.order.x as Order).deliverable_count + 1})
    if (this.parentDeliverables.list.length) {
      this.parentDeliverables.push(deliverable)
    }
    this.$router.push({
      name: `${this.baseName}DeliverableOverview`,
      params: {orderId: this.orderId + '', deliverableId: deliverable.id + '', username: this.$route.params.username},
    })
  }

  public addTags() {
    const tags = []
    const characters = []
    for (const char of this.characters.list) {
      const character = char.x as LinkedCharacter
      tags.push(...character.character.tags)
      characters.push(character.character)
    }
    this.addSubmission.fields.tags.update([...new Set(tags)])
    this.newInvoice.fields.characters.update(characters.map((char: Character) => char.id))
    this.viewSettings.patchers.characterInitItems.model = characters
  }

  public setReferences() {
    this.newInvoice.fields.references.update(
      this.references.list.map((x: SingleController<LinkedReference>) => {
        return x.x && x.x.reference.id
      }),
    )
  }

  public get invoiceEscrowDisabled() {
    if (!this.sellerHandler.artistProfile.x) {
      return true
    }
    if (this.newInvoice.fields.paid.value) {
      return true
    }
    return this.sellerHandler.artistProfile.x.escrow_disabled
  }

  public get keepReferences() {
    return Boolean(this.newInvoice.fields.references.value.length)
  }

  // Can't even get this to render during tests :/
  /* istanbul ignore next */
  public set keepReferences(val: boolean) {
    if (val) {
      this.setReferences()
    } else {
      this.newInvoice.fields.references.update([])
    }
  }

  public created() {
    this.deliverable.get().then(() => markRead(this.deliverable, 'sales.Deliverable')).then(
      () => this.parentDeliverables.replace(this.deliverable.x as Deliverable),
    ).catch(this.setError)
    this.characters.firstRun().then(this.addTags)
    this.revisions.firstRun().catch(this.statusOk(403))
    this.references.firstRun()
    // Used when adding the deliverable to keep state sane upstream.
    this.parentDeliverables = this.$getList(
      `order${this.orderId}__deliverables`, {endpoint: `${this.url}deliverables/`},
    )
    this.$listenForList(`${this.prefix}__characters`)
    this.$listenForList(`${this.prefix}__revisions`)
    this.$listenForList(`${this.prefix}__lineItems`)
    this.$listenForSingle(`${this.prefix}__rate__buyer`)
    this.$listenForSingle(`${this.prefix}__rate__seller`)
    this.$listenForSingle(`${this.prefix}__revision.*`)
    this.$listenForSingle('pricing')
    if (this.$route.query.showAdd) {
      this.viewSettings.patchers.showAddSubmission.model = true
    }
    if (this.$route.name === `${this.baseName}Deliverable`) {
      this.$router.replace({
        name: `${this.baseName}DeliverableOverview`,
        params: {...this.$route.params},
        query: {...this.$route.query},
        hash: this.$route.hash,
      })
    }
  }
}
</script>
