<template>
  <ac-load-section :controller="deliverable">
    <template v-slot:default>
      <v-container v-if="deliverable.x && order.x">
        <v-row>
          <v-col>
            <v-card>
              <v-card-title><h3>Now what?</h3></v-card-title>
              <ac-form>
                <ac-form-container @submit.prevent="stateChange.submitThen(updateDeliverable)"
                                   :errors="stateChange.errors" :sending="stateChange.sending">
                  <v-card-text>
                    <v-row dense>
                      <v-col v-if="is(DeliverableStatus.LIMBO) && isBuyer" cols="12">
                        <p>The artist has been informed about your order and should respond soon.</p>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.WAITING) && isBuyer" cols="12">
                        <p>Your order has been placed in the artist's waitlist. Waitlisted orders are not guaranteed by
                          Artconomy to be accepted in any order and every artist's policy is different in how they are
                          handled.
                          If your artist has not listed their waitlist policy for this commission in the product
                          details,
                          or in their commission info under the Overview tab, you may want to message them for
                          clarification.</p>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.WAITING) && isSeller && seller" cols="12">
                        <p>This order is in your waitlist. You should put your waitlist policy in your commission info
                          in your
                          <router-link :to="{name: 'Artist', params: {username: seller.username}}">Artist Settings
                          </router-link>
                          if you have not already, or else add it to the details of the product this order is associated
                          with.
                        </p>
                        <p>Hit the <strong>Select for Consideration</strong> button if you'd like to treat this as a
                          freshly placed order rather than having it chill in the waitlist.</p>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.NEW) && isBuyer" cols="12">
                        <p>Your order has been placed and is awaiting the artist's review. You will receive an email
                          when the
                          artist has accepted or rejected the order, or if they have any comments.</p>
                        <p>You may add additional comments or questions below!</p>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.NEW) && isSeller" cols="12">
                        <p>This order is pending your review. Please make any pricing adjustments and accept the order,
                          or
                          reject the order if you are unwilling or unable to complete the piece.</p>
                        <p>You may add comments to ask the commissioner questions.</p>
                      </v-col>
                      <v-col class="text-center" v-if="!is(DeliverableStatus.COMPLETED) && !isRegistered" cols="12">
                        <v-btn color="green" variant="flat" :to="registerLink" class="link-account">Link an Account</v-btn>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.PAYMENT_PENDING) && isBuyer" cols="12">
                        <v-divider/>
                        <p>
                          <strong>Congratulations!</strong> Your artist has accepted your order. Please submit payment
                          so that it can be added to their work queue.
                          <span v-if="paypalUrl">
                            <a :href="paypalUrl">Payment is done via PayPal.</a> This order is not protected by <router-link
                              :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield.</router-link>
                          </span>
                          <span
                              v-if="!deliverable.x.escrow_enabled">Your artist will inform you on how to pay them.</span>
                        </p>
                        <p v-if="deliverable.x.escrow_enabled">
                          <strong class="danger">WARNING:</strong> Only send payment using the <strong>'Send
                          Payment'</strong> button in the '<strong>Payment</strong>' <span
                            v-if="$vuetify.display.mdAndUp">tab</span><span v-else>dropdown option</span> directly below
                          this section.
                          Do not use any other method, button, or link, or we will not be able to protect you from
                          fraud. If your
                          artist asks for payment using another method, or if you are getting errors, please <a
                            @click="store.commit('supportDialog', true)">contact support.</a>
                        </p>
                      </v-col>
                      <v-col
                          v-if="isBuyer && deliverable.x.stream_link && !(is(DeliverableStatus.COMPLETED) || is(DeliverableStatus.CANCELLED) || is(DeliverableStatus.REFUNDED))"
                          cols="12">
                        <p><a :href="deliverable.x.stream_link" target="_blank">Your artist is streaming your commission
                          here!</a></p>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.PAYMENT_PENDING) && isSeller" cols="12">
                        <p>The commissioner has been informed that they must now pay in order for you to work on the
                          order.
                          You may continue to comment and tweak pricing in the interim, or you may cancel the order if
                          you need to.</p>
                        <p v-if="!deliverable.x.escrow_enabled && !paypalUrl">
                          <strong>REMEMBER:</strong> As we are not handling payment for this order, you MUST tell your
                          commissioner how to pay you. Leave a comment telling them how if you have not done so already.
                          When the customer has paid, click the 'Mark Paid' button.</p>
                        <p v-else-if="!deliverable.x.table_order">
                          You may mark this order as paid, if the customer has paid you through an outside method, or
                          you wish to waive payment for this commission.
                        </p>
                        <v-col class="text-center" v-if="!deliverable.x.escrow_enabled">
                          <v-btn color="primary" variant="flat" @click="statusEndpoint('mark-paid')()">Mark Paid</v-btn>
                        </v-col>
                        <ac-confirmation :action="statusEndpoint('mark-paid')" v-else-if="!deliverable.x.table_order">
                          <template v-slot:default="{on}">
                            <v-col class="text-center" cols="12">
                              <v-btn color="primary" variant="flat" v-on="on">Mark Paid</v-btn>
                            </v-col>
                          </template>
                          <template v-slot:confirmation-text>
                            <v-col>
                              <p>Artconomy will not be able to protect you from fraud if your customer has paid through
                                an outside
                                method.</p>
                              <p><strong>Don't do this unless you really know what you're doing!</strong></p>
                              <p>If you are having trouble, please contact support.</p>
                            </v-col>
                          </template>
                        </ac-confirmation>
                      </v-col>
                      <v-col v-if="isSeller && is(DeliverableStatus.REVIEW)" cols="12">
                        <p>The commissioner has been informed that the final is ready for their review. Please stand by
                          for final approval!</p>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.REVIEW) && deliverable.x.auto_finalize_on" cols="12">
                        <p>This order will auto-finalize on
                          <strong>{{ formatDateTerse(deliverable.x.auto_finalize_on) }}</strong>.</p>
                      </v-col>
                      <template v-if="isBuyer && is(DeliverableStatus.REVIEW)">
                        <v-col cols="12">
                          <p>Your artist has completed the piece! If all is well, please hit approve. Otherwise, if
                            there is an
                            issue you cannot resolve with the artist, please hit the dispute button.</p>
                        </v-col>
                        <v-row>
                          <v-col class="text-center">
                            <v-btn color="primary" @click="statusEndpoint('approve')()" variant="flat">Approve Final</v-btn>
                          </v-col>
                          <v-col class="text-center">
                            <v-btn color="danger" @click="statusEndpoint('dispute')()" variant="flat">File Dispute</v-btn>
                          </v-col>
                        </v-row>
                      </template>
                      <v-col class="text-center pt-2" cols="12" v-if="isBuyer && is(DeliverableStatus.DISPUTED)">
                        <p><strong>Your dispute has been filed.</strong> Please stand by for further instructions.
                          If you are able to work out your disagreement with the artist, please approve the order using
                          the
                          button below.</p>
                      </v-col>
                      <v-col class="text-center" v-if="(isBuyer || isArbitrator) && is(DeliverableStatus.DISPUTED)" cols="12">
                        <ac-confirmation :action="statusEndpoint('approve')">
                          <template v-slot:default="{on}">
                            <v-btn color="primary" v-on="on">Approve Final</v-btn>
                          </template>
                        </ac-confirmation>
                      </v-col>
                      <v-row v-if="is(DeliverableStatus.WAITING) || is(DeliverableStatus.NEW) || is(DeliverableStatus.PAYMENT_PENDING)">
                        <v-col class="text-center" v-if="is(DeliverableStatus.NEW) && canWaitlist && isSeller">
                          <v-btn color="secondary" @click="statusEndpoint('waitlist')()" variant="flat">Add to Waitlist</v-btn>
                        </v-col>
                        <v-col class="text-center" v-if="is(DeliverableStatus.WAITING) && isSeller">
                          <v-btn color="secondary" @click="statusEndpoint('make-new')()" variant="flat">Select for Consideration</v-btn>
                        </v-col>
                        <v-col class="text-center">
                          <ac-confirmation :action="statusEndpoint('cancel')">
                            <template v-slot:default="{on}">
                              <v-btn v-on="on" variant="elevated" color="black">Cancel Order</v-btn>
                            </template>
                          </ac-confirmation>
                        </v-col>
                        <v-col class="text-center">
                          <v-btn
                              color="primary" v-if="$route.params.deliverableId"
                              :to="{name: `${baseName}DeliverablePayment`,
                            params: {...$route.params}}"
                              @click="scrollToSection"
                              variant="flat"
                              class="review-terms-button"
                          >Review Terms/Pricing<span v-if="is(DeliverableStatus.PAYMENT_PENDING) && isBuyer">/Pay</span><span
                              v-else-if="(is(DeliverableStatus.WAITING) || is(DeliverableStatus.NEW)) && isSeller">/Accept</span></v-btn>
                        </v-col>
                        <v-col v-if="isBuyer" class="text-center">
                          <v-btn color="secondary" v-if="$route.params.deliverableId"
                                 variant="flat"
                                 :to="{name: `${baseName}DeliverableReferences`, params: {...$route.params}}">Add
                            References
                          </v-btn>
                        </v-col>
                      </v-row>
                      <v-col v-if="is(DeliverableStatus.QUEUED) && isBuyer" cols="12">
                        <p>Your order has been added to the artists queue. We will notify you when they have begun
                          work!</p>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.QUEUED) && isSeller" cols="12">
                        <p><strong>Excellent!</strong> The commissioner has paid<span v-if="escrow"> and the money is being held in safekeeping</span>.
                          When you've started work, hit the 'Mark In Progress' button to let the customer know.
                          You can also set the order's streaming link (if applicable) here:</p>
                      </v-col>
                      <v-col
                          v-if="deliverable.x.dispute_available_on && !(is(DeliverableStatus.DISPUTED) || is(DeliverableStatus.REVIEW) || is(DeliverableStatus.COMPLETED) || is(DeliverableStatus.REFUNDED))"
                          cols="12">
                        <p v-if="disputeTimeElapsed">You may file dispute for non-completion if needed.</p>
                        <p v-else>This order may be disputed for non-completion on:
                          <br/><strong>{{ formatDateTerse(deliverable.x.dispute_available_on) }}.</strong></p>
                        <v-col class="text-center">
                          <v-btn v-if="disputeTimeElapsed && isBuyer" @click="statusEndpoint('dispute')()"
                                 color="danger" variant="flat">File Dispute
                          </v-btn>
                        </v-col>
                      </v-col>
                      <v-col v-if="isSeller && (is(DeliverableStatus.QUEUED) || is(DeliverableStatus.IN_PROGRESS) || is(DeliverableStatus.REVIEW) || is(DeliverableStatus.DISPUTED))" cols="12">
                        <v-alert :value="order.x.private">
                          <strong>NOTE:</strong> This user has asked that this commission be private. Please do not use
                          a public streaming link!
                        </v-alert>
                        <ac-patch-field
                            :patcher="deliverable.patchers.stream_link" label="Stream URL">
                        </ac-patch-field>
                      </v-col>
                      <v-col v-if="isBuyer && is(DeliverableStatus.IN_PROGRESS)">
                        <p>The artist has begun work on your order. You'll be notified as they make progress!</p>
                      </v-col>
                      <v-col class="text-center" v-if="is(DeliverableStatus.QUEUED) && isSeller" cols="12">
                        <v-btn color="primary" @click="statusEndpoint('start')()" variant="flat">Mark In Progress</v-btn>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.DISPUTED) && isSeller">
                        <p><strong>This order is under dispute.</strong> One of our staff will be along soon to give
                          further
                          instruction. If you wish, you may refund the customer. Otherwise, please wait for our staff to
                          work
                          with you and the commissioner on a resolution.</p>
                      </v-col>
                      <v-col class="text-center" v-if="is(DeliverableStatus.COMPLETED)" cols="12">
                        <p>This order has been completed! <strong>Thank you for using Artconomy!</strong></p>
                      </v-col>
                      <v-col class="text-center" v-if="is(DeliverableStatus.COMPLETED) && disputeWindow && isBuyer && deliverable.x.auto_finalize_on" cols="12">
                        <v-alert :value="true" type="info">If there is an issue with this order, please <a href="#"
                          @click.prevent="store.commit('supportDialog', true)">contact
                          support</a>
                          on or before {{ formatDateTerse(deliverable.x.auto_finalize_on) }}.
                        </v-alert>
                      </v-col>
                      <v-col class="text-center" v-if="is(DeliverableStatus.REFUNDED)" cols="12">
                        <p>This order has been refunded and is now archived.</p>
                      </v-col>
                      <v-col class="text-center" v-if="isSeller && escrow && is(DeliverableStatus.COMPLETED)" cols="12">
                        <p>
                          <router-link :to="{name: 'Payout', params: {username: seller!.username}}">
                            If you have not already, please add your bank account in your payout settings.
                          </router-link>
                        </p>
                        <p>A transfer will automatically be initiated to your bank account.
                          Please wait up to five business days for payment to post.</p>
                      </v-col>
                      <v-col cols="12" v-if="deliverable.x.tip_invoice">
                        <ac-tipping-prompt
                            :invoice-id="deliverable.x.tip_invoice"
                            :source-lines="lineItems"
                            :username="buyer!.username"
                            :deliverable="deliverable"
                            :key="deliverable.x.tip_invoice"
                            :is-buyer="isBuyer"
                        />
                      </v-col>
                      <v-col cols="12" v-if="isBuyer && (is(DeliverableStatus.COMPLETED) || is(DeliverableStatus.REFUNDED))">
                        <ac-deliverable-rating end="seller" :order-id="orderId" :deliverable-id="deliverableId"
                                               key="seller"/>
                      </v-col>
                      <v-col cols="12" v-if="buyer && isSeller && (is(DeliverableStatus.COMPLETED) || is(DeliverableStatus.REFUNDED))">
                        <ac-deliverable-rating end="buyer" :order-id="orderId" :deliverable-id="deliverableId"
                                               key="buyer"/>
                      </v-col>
                      <v-col class="text-center" v-if="isSeller && is(DeliverableStatus.COMPLETED) && !order.x.private" cols="12">
                        <v-img :src="fridge" max-height="20vh" contain/>
                        <v-btn v-if="sellerSubmission" color="primary"
                               variant="flat"
                               :to="{name: 'Submission', params: {submissionId: sellerSubmission.id}}">Visit in
                          Gallery
                        </v-btn>
                        <v-btn color="green" v-else @click="addToGallery" class="gallery-add" variant="elevated">Add to my Gallery</v-btn>
                      </v-col>
                      <v-col class="text-center" v-if="isBuyer && is(DeliverableStatus.COMPLETED)" cols="12">
                        <v-img :src="fridge" max-height="20vh" contain/>
                        <v-btn v-if="buyerSubmission" color="primary"
                               variant="flat"
                               :to="{name: 'Submission', params: {submissionId: buyerSubmission.id}}">Visit in
                          Collection
                        </v-btn>
                        <v-btn color="green" v-else variant="elevated" @click="addToCollection" class="collection-add">Add to Collection
                        </v-btn>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.CANCELLED) && isBuyer">
                        <p>This order has been cancelled. You will have to create a new order if you want a
                          commission.</p>
                      </v-col>
                      <v-col v-if="is(DeliverableStatus.CANCELLED) && isSeller">
                        <p>This order has been cancelled. There is nothing more to do.</p>
                      </v-col>
                      <v-col v-if="!(is(DeliverableStatus.CANCELLED) || is(DeliverableStatus.REFUNDED) || is(DeliverableStatus.COMPLETED)) && escrow" cols="12">
                        <p><strong class="danger">WARNING:</strong> Any conversations made off-site, such as over
                          instant messanger or text, cannot be viewed or verified by Artconomy staff and will not be
                          considered in the case of a dispute. For your safety, any material discussion should be made
                          via comments on this order. If you must use instant messanger, copy a summary here of your
                          discussion for record, and have the other person affirm it is accurate.</p>
                      </v-col>
                      <ac-form-dialog
                          v-if="is(DeliverableStatus.COMPLETED) || isSeller"
                          @submit.prevent="addSubmission.submitThen(visitSubmission)"
                          v-model="viewSettings.patchers.showAddSubmission.model"
                          v-bind="addSubmission.bind"
                          :sending="addSubmission.sending"
                          :errors="addSubmission.errors"
                          :large="true"
                          :eager="true"
                          class="add-submission-dialog"
                          :title="isSeller ? 'Add to Gallery' : 'Add to Collection'"
                      >
                        <v-container class="pa-0">
                          <v-row no-gutters>
                            <v-col cols="12">
                              <ac-bound-field :field="addSubmission.fields.title" label="Title"/>
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
                              <ac-bound-field :field="addSubmission.fields.private" label="Private"
                                              field-type="ac-checkbox"
                                              hint="If checked, will not show this submission to anyone you've not explicitly shared it with."
                              />
                            </v-col>
                            <v-col cols="12" sm="6">
                              <ac-bound-field :field="addSubmission.fields.comments_disabled" label="Comments Disabled"
                                              field-type="ac-checkbox"
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
                          class="add-deliverable-dialog"
                          :title="'Add new Deliverable to Order.'"
                      >
                        <v-container class="pa-0">
                          <ac-invoice-form :new-invoice="newInvoice" :username="seller.username"
                                           :line-items="invoiceLineItems" :escrow-enabled="invoiceEscrowEnabled"
                                           :show-buyer="false">
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
                                                hint="Tag the character(s) to be referenced in this deliverable. If they're not listed on Artconomy, you can skip this step."/>
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
        <v-card>
          <ac-tab-nav :items="navItems" label="See more" />
        </v-card>
        <div class="section-scroll-target"></div>
        <router-view></router-view>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import Submission from '@/types/Submission.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcDeliverableRating from '@/components/views/order/AcDeliverableRating.vue'
import {RouteLocation, RouteLocationRaw, useRoute, useRouter} from 'vue-router'
import AcForm from '@/components/wrappers/AcForm.vue'
import Deliverable from '@/types/Deliverable.ts'
import {DeliverableProps, useDeliverable, ensureHandler} from './mixins/DeliverableMixin.ts'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import {VIEWER_TYPE} from '@/types/VIEWER_TYPE.ts'
import {Character} from '@/store/characters/types/Character.ts'
import AcInvoiceForm from '@/components/views/orders/AcInvoiceForm.vue'
import {SingleController} from '@/store/singles/controller.ts'
import LinkedReference from '@/types/LinkedReference.ts'
import {BASE_URL, formatDateTerse, markRead, parseISO} from '@/lib/lib.ts'
import {isBefore} from 'date-fns'
import AcTippingPrompt from '@/components/views/order/deliverable/AcTippingPrompt.vue'
import {ServicePlan} from '@/types/ServicePlan.ts'
import {computed, onMounted, watch} from 'vue'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import {useGoTo} from 'vuetify'
import {useViewer} from '@/mixins/viewer.ts'
import {usePricing} from '@/mixins/PricingAware.ts'
import {listenForSingle} from '@/store/singles/hooks.ts'
import {listenForList, useList} from '@/store/lists/hooks.ts'
import {setError, statusOk} from '@/mixins/ErrorHandling.ts'
import {useStore} from 'vuex'
import {useInvoicing} from '@/components/views/order/mixins/InvoicingMixin.ts'

const props = defineProps<{username: string} & DeliverableProps>()

const router = useRouter()
const route = useRoute()
const goTo = useGoTo()

const {
  order,
  deliverable,
  buyer,
  seller,
  escrow,
  isSeller,
  isBuyer,
  isArbitrator,
  is,
  newInvoice,
  lineItems,
  prefix,
  sellerHandler,
  arbitratorHandler,
  references,
  outputs,
  addSubmission,
  paypalUrl,
  viewMode,
  viewSettings,
  buyerSubmission,
  sellerSubmission,
  url,
  stateChange,
  statusEndpoint,
  characters,
  revisions,
  disputeWindow,
  updateDeliverable,
} = useDeliverable(props)

const {isRegistered, isStaff} = useViewer()

const {pricing} = usePricing()

const store = useStore()

const fridge = new URL('/static/images/fridge.png', BASE_URL).href

const parentDeliverables = useList(
  `order${props.orderId}__deliverables`,
  {endpoint: `${url.value}deliverables/`},
)

watch(() => deliverable.x?.id, () => {
  if (!deliverable.x) {
    return
  }
  if (deliverable.x.arbitrator) {
    ensureHandler(arbitratorHandler, deliverable.x.arbitrator)
  }
  outputs.makeReady(deliverable.x.outputs)
  addSubmission.fields.private.update(deliverable.x.order.private)
  newInvoice.fields.details.update(deliverable.x.details)
  newInvoice.fields.rating.update(deliverable.x.rating)
  order.setX(deliverable.x.order)
  order.ready = true
}, {immediate: true})

const setReferences = () => {
  newInvoice.fields.references.update(
    references.list.map((x: SingleController<LinkedReference>) => {
      return x.x && x.x.reference.id
    }),
  )
}

const viewerItems = computed(() => {
  const items = []
  if (viewMode.value === 0) {
    items.push({
      title: 'Please select...',
      value: VIEWER_TYPE.UNSET,
    })
  }
  items.push({title: 'Staff', value: VIEWER_TYPE.STAFF})
  if (buyer.value) {
    items.push({
      title: 'Buyer',
      value: VIEWER_TYPE.BUYER,
    })
  }
  items.push({
    title: 'Seller',
    value: VIEWER_TYPE.SELLER,
  })
  return items
})

const disputeTimeElapsed = computed(() => {
  /* istanbul ignore if */
  if (!deliverable.x?.dispute_available_on) {
    return false
  }
  return isBefore(parseISO(deliverable.x.dispute_available_on), new Date())
})

watch(() => references.list.length, setReferences)

const visitSubmission = (submission: Submission) => {
  return router.push({
    name: 'Submission',
    params: {submissionId: submission.id + ''},
    query: {editing: 'true'},
  })
}

const sellerName = computed(() => seller.value?.username || '')

const planName = computed(() => {
  // eslint-disable-next-line camelcase
  return seller.value?.service_plan
})

const registerLink = computed(() => {
  const baseRoute: RouteLocationRaw = {
    name: 'Register',
    query: {},
  }
  /* istanbul ignore if */
  if (!order.x) {
    return baseRoute
  }
  baseRoute.query!.claim = order.x.claim_token
  /* istanbul ignore next */
  const nextRoute: RouteLocationRaw = {
    name: route.name || undefined,
    params: {...route.params},
    query: {...route.query},
  }
  if (is(DeliverableStatus.COMPLETED)) {
    nextRoute.query!.showAdd = 'true'
  }
  baseRoute.query!.next = router.resolve(nextRoute).href
  return baseRoute
})

const navItems = computed(() => {
  const params = {...route.params}
  if (!params.deliverableId) {
    // We're transitioning to another area. Return no items.
    return []
  }
  return [
    {
      value: {
        name: `${props.baseName}DeliverableOverview`,
        params,
      },
      title: 'Overview',
    },
    {
      value: {
        name: `${props.baseName}DeliverableReferences`,
        params,
      },
      title: 'References/Characters',
    },
    {
      value: {
        name: `${props.baseName}DeliverablePayment`,
        params,
      },
      title: 'Payment/Terms',
    },
    {
      value: {
        name: `${props.baseName}DeliverableRevisions`,
        params,
      },
      title: 'Revisions/WIPs',
    },
  ]
})

const addToGallery = () => {
  addSubmission.fields.revision.update(null)
  viewSettings.model.showAddSubmission = true
}

const addToCollection = () => {
  if (isRegistered.value) {
    addSubmission.fields.revision.update(null)
    viewSettings.model.showAddSubmission = true
    return
  }
  router.push(registerLink.value)
}

const scrollToSection = () => {
  goTo('.section-scroll-target')
}

const visitDeliverable = (toVisit: Deliverable) => {
  order.updateX({deliverable_count: order.x!.deliverable_count + 1})
  parentDeliverables.push(toVisit)
  router.push({
    name: `${props.baseName}DeliverableOverview`,
    params: {
      orderId: props.orderId,
      deliverableId: toVisit.id + '',
      username: props.username,
    }
  })
}

const addTags = () => {
  const tags = []
  const theseCharacters: Character[] = []
  for (const char of characters.list) {
    const character = char.x
    tags.push(...character!.character.tags)
    theseCharacters.push(character!.character)
  }
  addSubmission.fields.tags.update([...new Set(tags)])
  newInvoice.fields.characters.update(theseCharacters.map((char: Character) => char.id))
  viewSettings.patchers.characterInitItems.model = theseCharacters
}

const international = computed(() => {
  // Note: This flag is currently used for new invoices based on the current deliverable-- I.E.,
  // multi-stage orders. This assumes the artist has not migrated to or from the US between creating
  // and issuing the next stage. This is such an edge case that I'm leaving this bug in for now,
  // however, it should be addressed when we refactor multi-stage orders to be more intuitive.
  return !!deliverable.x?.international
})

const canWaitlist = computed(() => {
  if (!planName.value) {
    return false
  }
  if (!pricing.x) {
    return false
  }
  return pricing.x.plans.filter((plan: ServicePlan) => plan.name === planName.value)[0].waitlisting
})

const invoiceEscrowEnabled = computed(() => {
  if (!sellerHandler.user.x || !sellerHandler.artistProfile.x) {
    return false
  }
  if (newInvoice.fields.paid.value) {
    return false
  }
  return sellerHandler.artistProfile.x.escrow_enabled
})

const keepReferences = computed({
  get: () => !!newInvoice.fields.references.value.length,
  set: (val: boolean) => {
    if (val) {
      setReferences()
      return
    } else {
      newInvoice.fields.references.update([])
  }
}})

listenForList(`${prefix.value}__characters`)
listenForList(`${prefix.value}__revisions`)
listenForList(`${prefix.value}__lineItems`)
listenForSingle(`${prefix.value}__rate__buyer`)
listenForSingle(`${prefix.value}__rate__seller`)
listenForSingle(`${prefix.value}__revision.*`)
listenForSingle(`${prefix.value}__clientSecret`)
listenForSingle('new-revision-file')

// At the moment, this isn't much benefit, since dropping a file on the uploader immediately submits.
// But if I change the default behavior, not having this will introduce a subtle bug where the contents will
// disappear if we navigate away.
listenForSingle('new-reference-file')

watch(route, (route: RouteLocation) => {
  if (route.name !== `${props.baseName}Deliverable`) {
    return
  }
  router.replace({
    name: `${props.baseName}DeliverableOverview`,
    params: {...route.params},
    query: {...route.query},
    hash: route.hash,
  }).then()
}, {immediate: true})

const {invoiceLineItems} = useInvoicing({
  newInvoice, invoiceEscrowEnabled, international, planName, sellerName,
})

onMounted(() => {
  if (route.query.showAdd) {
    viewSettings.patchers.showAddSubmission.model = true
  }
  deliverable.get().then(() => markRead(deliverable, 'sales.Deliverable')).then(
    () => parentDeliverables.replace(deliverable.x as Deliverable),
  ).catch(setError)
  characters.firstRun().then(addTags)
  revisions.firstRun().catch(statusOk(403))
  references.firstRun()
})
</script>
