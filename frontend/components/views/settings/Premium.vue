<template>
  <v-card>
    <v-card-text>
      <v-layout row wrap v-if="!subject.portrait && !subject.landscape">
        <v-flex xs12 text-xs-center>
          <p>Premium settings are only available with a portrait or Landscape subscription.</p>
          <v-btn :to="{name: 'Upgrade'}" color="secondary">Upgrade Now!</v-btn>
        </v-flex>
      </v-layout>
      <v-layout row wrap v-if="portrait">
        <v-flex xs12>
          <v-subheader>Portrait settings</v-subheader>
          <p>Manage your portrait settings here. You will be notified when artists you are watching become available.
            <strong>Want to get notified on Telegram?</strong> Link your Telegram account!</p>
        </v-flex>
        <v-flex text-xs-center xs12 sm4 offset-sm4 d-flex>
          <a :href="subject.telegram_link" target="_blank" style="text-decoration: none">
            <v-card class="elevation-7 setup-telegram">
              <v-card-text>
                <v-layout row wrap>
                  <v-flex xs6 sm12 order-xs2 order-sm1 px-2>
                    <img src="/static/images/telegram_logo.svg" style="height: 10vh" alt="Telegram logo"/>
                  </v-flex>
                  <v-flex xs6 sm12 order-xs1 order-sm2 class="two-factor-label">
                    <p>Click this panel, then click the 'start' button in Telegram to link your account!</p>
                  </v-flex>
                </v-layout>
              </v-card-text>
            </v-card>
          </a>
        </v-flex>
      </v-layout>
      <v-layout row wrap v-if="subject.landscape">
        <v-flex xs12 text-xs-center>
          <v-subheader>Landscape settings</v-subheader>
          <p>There are no special settings to configure for Landscape at this time. Your commission bonuses will be applied automatically!</p>
        </v-flex>
      </v-layout>
      <v-layout row wrap v-if="(subject.portrait || subject.landscape)">
        <v-flex xs12 text-xs-center>
          <p>Your {{subscriptionType}} subscription is paid through {{formatDate(paidThrough)}}.</p>
        </v-flex>
        <v-flex xs12 sm6 text-xs-center>
          <v-btn :to="{name: 'Payment', params: {username}}" color="primary">Update Payment Settings</v-btn>
        </v-flex>
        <v-flex xs12 sm6 text-xs-center v-if="subject.portrait_enabled || subject.landscape_enabled">
          <ac-confirmation :action="cancelSubscription">
            <template v-slot:default="{on}">
              <v-btn color="danger" class="cancel-subscription" v-on="on">Cancel Subscription</v-btn>
            </template>
            <span slot="confirmation-text">
              <p>Are you sure you wish to cancel your subscription?</p>
              <p>Note: You will be able to use the extra features until your current term ends.</p>
            </span>
          </ac-confirmation>
        </v-flex>
        <v-flex xs12 sm6 text-xs-center v-else-if="subject.portrait || subject.landscape">
          <v-btn color="secondary" :to="{name: 'Upgrade'}">Restart Subscription</v-btn>
        </v-flex>
      </v-layout>
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
