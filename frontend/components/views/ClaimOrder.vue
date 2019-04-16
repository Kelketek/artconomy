<template>
  <v-container>
    <ac-form-container :sending="claimForm.sending" :errors="claimForm.errors">
      <v-layout row wrap>
        <v-flex xs12 text-xs-center>
          <h1>Your Order is waiting!</h1>
        </v-flex>
        <v-flex xs12 text-xs-center>
          <v-img src="/static/images/cheering.png" max-height="30vh" :contain="true"></v-img>
        </v-flex>
        <v-flex xs12 v-if="isRegistered" text-xs-center>
          <p>You are currently logged in as <strong>{{viewerName}}</strong>. Would you like to claim this order as {{viewerName}} or continue as a guest?</p>
        </v-flex>
        <v-flex xs12 sm6 v-if="isRegistered" text-xs-center text-sm-right>
          <v-btn color="green" @click="claimAsUser">Claim as {{viewerName}}!</v-btn>
        </v-flex>
        <v-flex xs12 sm6 v-if="isRegistered" text-xs-center text-sm-left>
          <v-btn @click="becomeGuest">Continue as guest</v-btn>
        </v-flex>
        <v-flex xs12 v-for="field of claimForm.fields" :key="field.name">
          <v-alert v-for="(error, index) of field.errors" :key="index" :value="true">
            {{error}}
          </v-alert>
        </v-flex>
      </v-layout>
    </ac-form-container>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import {Prop} from 'vue-property-decorator'
import {artCall} from '@/lib'
import {RawLocation} from 'vue-router'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {FormController} from '@/store/forms/form-controller'
import {User} from '@/store/profiles/types/User'

@Component({
  components: {AcFormContainer, AcLoadingSpinner},
})
export default class ClaimOrder extends mixins(Viewer) {
  @Prop()
  public username!: string
  @Prop()
  public orderId!: string
  @Prop()
  public token!: string
  public claimForm: FormController = null as unknown as FormController
  public failed = false

  public visitOrder(user: User) {
    const route: RawLocation = {name: 'Order', params: {orderId: this.orderId, username: this.rawViewerName}}
    const commentId = this.$route.query.commentId
    if (commentId) {
      route.query = {commentId}
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

  public created() {
    this.claimForm = this.$getForm('orderClaim', {
      endpoint: '/api/sales/v1/order-auth/',
      fields: {
        id: {value: this.orderId},
        claim_token: {value: this.token},
        chown: {value: false},
      },
    })
    if (!this.isRegistered) {
      this.claimForm.submitThen(this.visitOrder)
    }
  }
}
</script>
