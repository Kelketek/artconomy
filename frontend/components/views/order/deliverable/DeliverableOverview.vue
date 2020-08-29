<template>
  <ac-load-section :controller="deliverable">
    <template v-slot:default v-if="seller">
      <v-row>
        <v-col cols="12" sm="6" md="4">
          <v-toolbar dense color="black">
            <ac-avatar :user="order.x.seller" :show-name="false" />
            <v-toolbar-title class="ml-1"><ac-link :to="profileLink(order.x.seller)">{{order.x.seller.username}}</ac-link></v-toolbar-title>
          </v-toolbar>
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken2">
            <v-card-text >
              <v-row dense>
                <v-col class="py-2 subheading" cols="12" >
                  <ac-link :to="product && {name: 'Product', params: {username: product.user.username, productId: product.id}}">{{name}}</ac-link>
                </v-col>
                <v-col cols="6" md="12">
                  <ac-asset :asset="deliverable.x.display" thumb-name="thumbnail" />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="8">
          <v-toolbar dense color="black" v-if="order.x.buyer">
            <ac-avatar :user="order.x.buyer" :show-name="false" />
            <v-toolbar-title class="ml-1"><ac-link :to="profileLink(order.x.buyer)">{{deriveDisplayName(order.x.buyer.username)}}</ac-link></v-toolbar-title>
          </v-toolbar>
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken2">
            <v-card-text>
              <v-row dense>
                <v-col align-self="center">
                  <h2><span v-if="isSeller">Sale</span>
                    <span v-else-if="isArbitrator">Case</span>
                    <span v-else>Order</span>
                    #{{order.x.id}} <span v-if="!isSeller || !(is(NEW) || is(PAYMENT_PENDING))">- [{{deliverable.x.name}}] Details:</span></h2>
                  <ac-patch-field :patcher="deliverable.patchers.name" label="Deliverable Name" v-if="isSeller && (is(NEW) || is(PAYMENT_PENDING))"></ac-patch-field>
                </v-col>
                <v-col class="text-right" align-self="center">
                  <v-chip color="white" light v-if="order.x.private" class="ma-1">
                    <v-icon left>visibility_off</v-icon>
                    Private
                  </v-chip>
                  <ac-deliverable-status :deliverable="deliverable.x" class="ma-1" />
                  <v-btn class="ma-1 rating-button pa-1" small :color="ratingColor[deliverable.x.rating]" :ripple="false">
                    {{ratingsShort[deliverable.x.rating]}}
                  </v-btn>
                </v-col>
              </v-row>
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
              <v-row>
                <v-col class="text-center" v-if="isSeller && seller.landscape">
                  <v-btn color="green" class="add-deliverable" @click="viewSettings.patchers.showAddDeliverable.model = true">Add Stage/Deliverable</v-btn>
                </v-col>
                <v-col class="text-center" v-if="order.x.deliverable_count > 1">
                  <v-btn color="primary" :to="{name: baseName, params: {orderId, username: $route.params.username}}">See All Deliverables</v-btn>
                </v-col>
              </v-row>
              <ac-rendered :value="deliverable.x.details" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col cols="12" v-if="$vuetify.breakpoint.mdAndUp">
          <ac-comment-section :commentList="comments" :nesting="false" :locked="!isInvolved" :guest-ok="true" :show-history="isArbitrator" />
        </v-col>
      </v-row>
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
              <a href="#" @click.prevent="setSupport(true)">please contact support</a> or ask for help in the <a href="https://discord.gg/4nWK9mf" target="_blank">Artconomy Discord</a>.</p>
            <p>Your artist will contact you soon to confirm acceptance of your commission, or ask additional questions.</p>
          </v-col>
        </v-row>
      </ac-expanded-property>
      <ac-comment-section :commentList="comments" :nesting="false" :locked="!isInvolved" :guest-ok="true" :show-history="isArbitrator" v-if="$vuetify.breakpoint.smAndDown" />
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import DeliverableMixin from '@/components/views/order/mixins/DeliverableMixin'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
import AcAsset from '@/components/AcAsset.vue'
import Formatting from '@/mixins/formatting'
import AcDeliverableStatus from '@/components/AcDeliverableStatus.vue'
import AcRendered from '@/components/wrappers/AcRendered'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Ratings from '@/mixins/ratings'
import AcBoundField from '@/components/fields/AcBoundField'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Order from '@/types/Order'
import {Watch} from 'vue-property-decorator'
import AcAvatar from '@/components/AcAvatar.vue'
@Component({
  components: {
    AcAvatar,
    AcLink,
    AcExpandedProperty,
    AcCommentSection,
    AcConfirmation,
    AcFormDialog,
    AcBoundField,
    AcPatchField,
    AcFormContainer,
    AcForm,
    AcRendered,
    AcDeliverableStatus,
    AcAsset,
    AcEscrowLabel,
    AcLoadSection,
  },
})
export default class DeliverableOverview extends mixins(DeliverableMixin, Formatting, Ratings) {
  public showConfirm = false
  public inviteSent = false

  @Watch('order.patchers.customer_email.model')
  public resetSent() {
    this.inviteSent = false
  }

  public get inviteDisabled() {
    /* istanbul ignore if */
    if (!this.order.x) {
      return true
    }
    const value = this.order.patchers.customer_email.model
    return (this.inviteSent || !value || value !== this.order.x.customer_email)
  }

  public markInviteSent(order: Order) {
    this.inviteSent = true
    this.order.setX(order)
  }

  public created() {
    if (this.$route.query.showConfirm) {
      this.showConfirm = true
    }
  }
}
</script>
