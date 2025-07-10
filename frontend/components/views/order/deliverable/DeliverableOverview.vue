<template>
  <ac-load-section :controller="deliverable">
    <template #default>
      <v-row v-if="seller && deliverable.x && order.x">
        <v-col cols="12" sm="6" md="4">
          <v-toolbar dense color="black">
            <ac-avatar :user="order.x.seller" :show-name="false" class="ml-3" />
            <v-toolbar-title class="ml-1">
              <ac-link :to="profileLink(order.x.seller)">
                {{ order.x.seller.username }}
              </ac-link>
            </v-toolbar-title>
          </v-toolbar>
          <v-card :color="current.colors['well-darken-2']">
            <v-card-text>
              <v-row dense>
                <v-col class="py-2 subheading" cols="12">
                  <ac-link
                    :to="
                      product && {
                        name: 'Product',
                        params: {
                          username: product.user.username,
                          productId: product.id,
                        },
                      }
                    "
                  >
                    {{ name }}
                  </ac-link>
                </v-col>
                <v-col cols="6" md="12">
                  <ac-asset
                    :asset="deliverable.x!.display"
                    thumb-name="thumbnail"
                    alt=""
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="8">
          <v-toolbar v-if="order.x.buyer" dense color="black">
            <ac-avatar :user="order.x.buyer" :show-name="false" class="ml-3" />
            <v-toolbar-title class="ml-1">
              <ac-link :to="profileLink(order.x.buyer)">
                {{ deriveDisplayName(order.x.buyer.username) }}
              </ac-link>
              <span v-if="order.x.guest_email && isSeller">
                ({{ order.x.guest_email }})</span
              >
            </v-toolbar-title>
          </v-toolbar>
          <v-card :color="current.colors['well-darken-2']">
            <v-card-text>
              <v-row dense>
                <v-col cols="12" md="9" order="1">
                  <h2>
                    <span v-if="isSeller">Sale</span>
                    <span v-else-if="isArbitrator">Case</span>
                    <span v-else>Order</span>
                    #{{ order.x.id }}
                    <span v-if="!isSeller || !is(s.NEW, s.WAITING)"
                      >- [{{ deliverable.x.name }}] Details:</span
                    >
                  </h2>
                  <ac-patch-field
                    v-if="isSeller && is(s.NEW, s.WAITING)"
                    :patcher="deliverable.patchers.name"
                    label="Deliverable Name"
                  />
                </v-col>
                <v-col v-if="isSeller" cols="12" md="12" order="2" order-md="3">
                  <ac-patch-field
                    :patcher="order.patchers.hide_details"
                    field-type="v-checkbox"
                    label="Hide Details"
                    :disabled="order.x.private"
                    :persistent-hint="true"
                    hint="If your public queue is enabled in your Artist Settings,
                            hides the details of this order as if it were a private order.
                            Automatically enabled if this order is a private one."
                  />
                </v-col>
                <v-col
                  cols="12"
                  md="3"
                  class="text-md-right text-center"
                  order="3"
                  order-md="2"
                  align-self="center"
                >
                  <v-chip
                    v-if="order.x.private"
                    color="white"
                    variant="flat"
                    light
                    class="ma-1"
                  >
                    <v-icon left :icon="mdiEyeOff" />
                    Private
                  </v-chip>
                  <ac-deliverable-status
                    :deliverable="deliverable.x"
                    class="ma-1"
                  />
                  <v-btn
                    class="ma-1 rating-button pa-1"
                    variant="flat"
                    small
                    :color="RATING_COLOR[deliverable.x.rating]"
                    :ripple="editable"
                    @click="showRating"
                  >
                    <v-icon v-if="editable" left :icon="mdiPencil" />
                    {{ RATINGS_SHORT[deliverable.x.rating] }}
                  </v-btn>
                  <ac-expanded-property v-model="ratingDialog">
                    <ac-patch-field
                      field-type="ac-rating-field"
                      :patcher="deliverable.patchers.rating"
                    />
                  </ac-expanded-property>
                </v-col>
              </v-row>
              <v-col
                v-if="
                  isSeller &&
                  (unregisteredBuyer || guestBuyer) &&
                  !is(s.COMPLETED, s.DISPUTED, s.REFUNDED, s.CANCELLED)
                "
                cols="12"
              >
                <ac-patch-field
                  :patcher="order.patchers.customer_display_name"
                  hint="Enter a name to show on your order page to help you remember who ordered this. If the user
                    registers, we will use their username instead."
                  label="Display name"
                />
                <ac-form
                  v-if="unregisteredBuyer"
                  @submit.prevent="orderEmail.submitThen(markInviteSent)"
                >
                  <ac-form-container v-bind="orderEmail.bind">
                    <v-row dense class="justify-content" align-content="center">
                      <v-col>
                        <ac-patch-field
                          label="Customer email address"
                          hint="Set and save this to send the customer an invite link."
                          :persistent-hint="true"
                          :patcher="order.patchers.customer_email"
                          :disabled="verifiedEmail"
                          :refresh="false"
                        />
                        <small v-if="verifiedEmail"
                          >Email verified. It may no longer be changed.</small
                        >
                      </v-col>
                      <v-col class="shrink d-flex" align-self="center">
                        <v-btn
                          :disabled="inviteDisabled"
                          color="primary"
                          type="submit"
                          variant="flat"
                          class="send-invite-button"
                        >
                          Send Invite Link
                        </v-btn>
                      </v-col>
                    </v-row>
                    <v-row no-gutters>
                      <v-col cols="12">
                        <v-alert
                          v-model="inviteSent"
                          :dismissible="true"
                          type="success"
                        >
                          Invite email sent!
                        </v-alert>
                      </v-col>
                    </v-row>
                  </ac-form-container>
                </ac-form>
              </v-col>
              <v-row>
                <v-col v-if="isSeller && seller.landscape" class="text-center">
                  <v-btn
                    color="green"
                    variant="flat"
                    class="add-deliverable"
                    @click="
                      viewSettings.patchers.showAddDeliverable.model = true
                    "
                  >
                    Add Stage/Deliverable
                  </v-btn>
                </v-col>
                <v-col v-if="order.x.deliverable_count > 1" class="text-center">
                  <v-btn
                    color="primary"
                    variant="flat"
                    :to="{
                      name: baseName,
                      params: { orderId, username: route.params.username },
                    }"
                  >
                    See All Deliverables
                  </v-btn>
                </v-col>
              </v-row>
              <v-card-text>
                <v-row dense>
                  <v-col cols="12">
                    <v-divider />
                  </v-col>
                  <v-col cols="12">
                    <h2>
                      Details:
                      <v-btn
                        v-show="!editDetails && editable"
                        icon="mdi-pencil"
                        variant="plain"
                        @click="editDetails = true"
                      >
                        <v-icon :icon="mdiPencil" />
                      </v-btn>
                    </h2>
                  </v-col>
                  <v-col cols="12">
                    <ac-patch-field
                      v-if="editable && editDetails"
                      :patcher="deliverable.patchers.details"
                      field-type="ac-editor"
                    />
                    <ac-rendered v-else :value="deliverable.x.details" />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col v-if="isSeller" cols="12">
          <v-card>
            <v-card-text>
              <ac-patch-field
                :patcher="deliverable.patchers.notes"
                field-type="ac-editor"
                label="Notes"
                :persistent-hint="true"
                :counter="5000"
                hint="Notes on this deliverable.
                  These are not shown to the client, but can be used to write down any notes you need for your
                  own records."
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col v-if="$vuetify.display.mdAndUp" cols="12">
          <ac-comment-section
            :comment-list="comments"
            :nesting="false"
            :locked="!isInvolved"
            :guest-ok="true"
            :show-history="isArbitrator"
          />
        </v-col>
      </v-row>
      <ac-expanded-property v-model="showConfirm">
        <template #title> We're on it! </template>
        <v-row align="center" class="order-confirmation justify-content-center">
          <v-col cols="12" sm="6" md="3" align-self="center">
            <v-img
              :src="cheering"
              :contain="true"
              max-height="30vh"
              alt="Hooray! The order has been placed."
              :eager="prerendering"
            />
          </v-col>
          <v-col cols="12" sm="6" md="9" align-self="center">
            <h1 class="display-1 mb-4">Order Placed.</h1>
            <h2 class="headline mb-2">Check your email!</h2>
            <p>
              We've sent a confirmation to your email address. If you haven't
              received it, please check your spam folder.
            </p>
            <p>
              <strong
                >It is very important that you verify you're getting emails from
                Artconomy, or else your artist won't be able to send you
                messages on their progress.</strong
              >
              If you're having trouble,
              <a href="#" @click.prevent="store.commit('supportDialog', true)"
                >please contact support</a
              >
              or ask for help in the
              <a href="https://discord.gg/4nWK9mf" target="_blank"
                >Artconomy Discord</a
              >.
            </p>
            <p>
              Your artist will contact you soon to confirm acceptance of your
              commission, or ask additional questions.
            </p>
          </v-col>
        </v-row>
      </ac-expanded-property>
      <ac-comment-section
        v-if="smAndDown"
        :comment-list="comments"
        :nesting="false"
        :locked="!isInvolved || is(s.LIMBO, s.MISSED)"
        :guest-ok="true"
        :show-history="isArbitrator"
      />
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import {
  DeliverableProps,
  useDeliverable,
} from "@/components/views/order/mixins/DeliverableMixin.ts"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcAsset from "@/components/AcAsset.vue"
import AcDeliverableStatus from "@/components/AcDeliverableStatus.vue"
import AcRendered from "@/components/wrappers/AcRendered.ts"
import AcForm from "@/components/wrappers/AcForm.vue"
import AcFormContainer from "@/components/wrappers/AcFormContainer.vue"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import AcCommentSection from "@/components/comments/AcCommentSection.vue"
import AcExpandedProperty from "@/components/wrappers/AcExpandedProperty.vue"
import AcLink from "@/components/wrappers/AcLink.vue"
import AcAvatar from "@/components/AcAvatar.vue"
import { BASE_URL, RATING_COLOR, RATINGS_SHORT } from "@/lib/lib.ts"
import { ref, watch, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { useStore } from "vuex"
import { DeliverableStatus as s } from "@/types/enums/DeliverableStatus.ts"
import { usePrerendering } from "@/mixins/prerendering.ts"
import { deriveDisplayName } from "@/lib/otherFormatters.ts"
import { mdiEyeOff, mdiPencil } from "@mdi/js"
import { profileLink } from "@/lib/otherFormatters.ts"
import { useDisplay, useTheme } from "vuetify"
import type { Order } from "@/types/main"
import { User } from "@/store/profiles/types/main"

const props = defineProps<DeliverableProps>()

const showConfirm = ref(false)
const inviteSent = ref(false)
const editDetails = ref(false)
const ratingDialog = ref(false)
const cheering = new URL("/static/images/cheering.png", BASE_URL).href
const { current } = useTheme()
const { smAndDown } = useDisplay()

const route = useRoute()
const store = useStore()
const {
  order,
  deliverable,
  editable,
  product,
  buyer,
  seller,
  name,
  isSeller,
  isArbitrator,
  isInvolved,
  comments,
  orderEmail,
  viewSettings,
  is,
} = useDeliverable(props)

watch(
  () => order.patchers.customer_email.model,
  () => {
    inviteSent.value = false
  },
)

watch(editable, (val: boolean) => {
  if (!val) {
    editDetails.value = false
    ratingDialog.value = false
  }
})

const showRating = () => {
  if (editable.value) {
    ratingDialog.value = true
  }
}

const unregisteredBuyer = computed(
  () => !buyer.value || (buyer.value as User).verified_email,
)

const guestBuyer = computed(() => buyer.value && (buyer.value as User).guest)

const verifiedEmail = computed(
  () => buyer.value && (buyer.value as User).verified_email,
)

const inviteDisabled = computed(() => {
  if (!order.x) {
    return true
  }
  const value = order.patchers.customer_email.model
  return inviteSent.value || !value || value !== order.x.customer_email
})

const markInviteSent = (ourOrder: Order) => {
  inviteSent.value = true
  order.setX(ourOrder)
}

const { prerendering } = usePrerendering()

onMounted(() => {
  if (route.query.showConfirm) {
    showConfirm.value = true
  }
})
</script>
