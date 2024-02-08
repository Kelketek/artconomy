<template>
  <v-container>
    <ac-form-container :sending="claimForm.sending" :errors="claimForm.errors">
      <v-row no-gutters>
        <v-col class="text-center" cols="12">
          <h1>Your Order is waiting!</h1>
        </v-col>
        <v-col class="text-center" cols="12">
          <v-img :src="cheering" max-height="30vh" :contain="true"></v-img>
        </v-col>
        <v-col class="text-center" cols="12" v-if="isRegistered">
          <p>You are currently logged in as <strong>{{viewerName}}</strong>. Would you like to claim this order as
            {{viewerName}} or continue as a guest?</p>
        </v-col>
        <v-col class="text-center text-sm-right" cols="12" sm="6" v-if="isRegistered">
          <v-btn color="green" @click="claimAsUser" variant="flat">Claim as {{viewerName}}!</v-btn>
        </v-col>
        <v-col class="text-center text-sm-left" cols="12" sm="6" v-if="isRegistered">
          <v-btn @click="becomeGuest" variant="flat">Continue as guest</v-btn>
        </v-col>
        <v-col cols="12" v-for="field of claimForm.fields" :key="field.fieldName">
          <v-alert v-for="(error, index) of field.errors" :key="index" :value="true">
            {{error}}
          </v-alert>
        </v-col>
      </v-row>
    </ac-form-container>
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import {RouteLocationRaw} from 'vue-router'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import {User} from '@/store/profiles/types/User.ts'
import {BASE_URL} from '@/lib/lib.ts'

@Component({
  components: {
    AcFormContainer,
    AcLoadingSpinner,
  },
})
class ClaimOrder extends mixins(Viewer) {
  @Prop()
  public username!: string

  @Prop()
  public orderId!: string

  @Prop()
  public token!: string

  @Prop()
  public deliverableId!: string

  @Prop()
  public next!: string

  public claimForm: FormController = null as unknown as FormController
  public failed = false

  public cheering = new URL('static/images/cheering.png', BASE_URL).href

  public visitOrder(user: User) {
    this.$sock.socket?.reconnect()
    const route: RouteLocationRaw = {}
    if (this.next) {
      Object.assign(route, JSON.parse(this.next) as RouteLocationRaw)
      if (route.query === undefined) {
        route.query = {}
      }
    } else {
      Object.assign(route, {
        name: 'Order',
        params: {
          orderId: this.orderId,
          username: this.rawViewerName,
        },
      })
      if (this.deliverableId) {
        Object.assign(route, {
          name: 'OrderDeliverableOverview',
          params: {
            orderId: this.orderId,
            deliverableId: this.deliverableId,
            username: this.rawViewerName,
          },
        })
      }
    }
    const commentId = this.$route.query.commentId
    if (commentId) {
      route.query!.commentId = commentId
    }
    this.viewerHandler.user.setX(user)
    if (user.guest) {
      this.viewerHandler.artistProfile.kill()
      this.viewerHandler.artistProfile.setX(null)
      this.viewerHandler.artistProfile.ready = false
      this.viewerHandler.artistProfile.fetching = false
    }
    this.$router.replace(route)
  }

  public claimAsUser() {
    this.claimForm.fields.chown.update(true)
    this.claimForm.submitThen(this.visitOrder)
  }

  public becomeGuest() {
    this.claimForm.fields.chown.update(false)
    this.claimForm.submitThen(this.visitOrder)
  }

  public sendForm() {
    if (!this.isRegistered) {
      this.claimForm.submitThen(this.visitOrder)
    }
  }

  public created() {
    this.claimForm = this.$getForm('orderClaim', {
      endpoint: '/api/sales/order-auth/',
      reset: false,
      fields: {
        id: {value: this.orderId},
        claim_token: {value: this.token},
        chown: {value: false},
      },
    })
    this.$sock.connectListeners.ClaimOrder = this.sendForm
  }
}

export default toNative(ClaimOrder)
</script>
