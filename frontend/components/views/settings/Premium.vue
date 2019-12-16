<template>
  <v-card>
    <v-card-text>
      <v-row no-gutters   v-if="!subject.portrait && !subject.landscape">
        <v-col class="text-center" cols="12" >
          <p>Premium settings are only available with a portrait or Landscape subscription.</p>
          <v-btn :to="{name: 'Upgrade'}" color="secondary">Upgrade Now!</v-btn>
        </v-col>
      </v-row>
      <v-row no-gutters   v-if="portrait">
        <v-col cols="12">
          <v-subheader>Portrait settings</v-subheader>
          <p>Manage your portrait settings here. You will be notified when artists you are watching become available.
            <strong>Want to get notified on Telegram?</strong> Link your Telegram account!</p>
        </v-col>
        <v-col class="text-center d-flex" cols="12" sm="4" offset-sm="4" >
          <a :href="subject.telegram_link" target="_blank" style="text-decoration: none">
            <v-card class="elevation-7 setup-telegram">
              <v-card-text>
                <v-row no-gutters  >
                  <v-col class="px-2" cols="6" sm="12" order="2" order-sm="1" >
                    <img src="/static/images/telegram_logo.svg" style="height: 10vh" alt="Telegram logo"/>
                  </v-col>
                  <v-col cols="6" sm="12" order="1" order-sm="2" class="two-factor-label">
                    <p>Click this panel, then click the 'start' button in Telegram to link your account!</p>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </a>
        </v-col>
      </v-row>
      <v-row no-gutters   v-if="subject.landscape">
        <v-col class="text-center" cols="12" >
          <v-subheader>Landscape settings</v-subheader>
          <p>There are no special settings to configure for Landscape at this time. Your commission bonuses will be applied automatically!</p>
        </v-col>
      </v-row>
      <v-row no-gutters   v-if="(subject.portrait || subject.landscape)">
        <v-col class="text-center" cols="12" >
          <p>Your {{subscriptionType}} subscription is paid through {{formatDate(paidThrough)}}.</p>
        </v-col>
        <v-col class="text-center" cols="12" sm="6" >
          <v-btn :to="{name: 'Payment', params: {username}}" color="primary">Update Payment Settings</v-btn>
        </v-col>
        <v-col class="text-center" cols="12" sm="6" v-if="subject.portrait_enabled || subject.landscape_enabled">
          <ac-confirmation :action="cancelSubscription">
            <template v-slot:default="{on}">
              <v-btn color="danger" class="cancel-subscription" v-on="on">Cancel Subscription</v-btn>
            </template>
            <span slot="confirmation-text">
              <p>Are you sure you wish to cancel your subscription?</p>
              <p>Note: You will be able to use the extra features until your current term ends.</p>
            </span>
          </ac-confirmation>
        </v-col>
        <v-col class="text-center" cols="12" sm="6" v-else-if="subject.portrait || subject.landscape">
          <v-btn color="secondary" :to="{name: 'Upgrade'}">Restart Subscription</v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import Subjective from '@/mixins/subjective'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcTagField from '@/components/fields/AcTagField.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {artCall} from '@/lib'
import {User} from '@/store/profiles/types/User'
import Formatting from '@/mixins/formatting'

@Component({
  components: {AcConfirmation, AcCardManager, AcTagField, AcLoadingSpinner, AcPatchField},
})
export default class Premium extends mixins(Viewer, Subjective, Formatting) {
  public cancelSubscription() {
    artCall({url: `/api/sales/v1/account/${this.username}/cancel-premium/`, method: 'post'}).then(
      this.subjectHandler.user.setX,
    )
  }
  public get subscriptionType() {
    const subject = this.subject as User
    /* istanbul ignore if */
    if (!this.subject) {
      return ''
    }
    if (subject.landscape) {
      return 'Landscape'
    }
    /* istanbul ignore else */
    if (subject.portrait) {
      return 'Portrait'
    }
  }
  public get paidThrough() {
    const subject = this.subject as User
    /* istanbul ignore if */
    if (!this.subject) {
      return null
    }
    if (subject.landscape) {
      return subject.landscape_paid_through
    }
    /* istanbul ignore else */
    if (subject.portrait) {
      return subject.portrait_paid_through
    }
  }
}
</script>
