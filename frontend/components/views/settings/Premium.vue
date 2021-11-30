<template>
  <v-card>
    <v-card-text>
      <v-row no-gutters v-if="!subject.landscape">
        <v-col class="text-center" cols="12" >
          <p>Premium settings are only available with a Landscape subscription.</p>
          <v-btn :to="{name: 'Upgrade'}" color="secondary">Upgrade Now!</v-btn>
        </v-col>
      </v-row>
      <v-row no-gutters v-if="subject.landscape">
        <v-col class="text-center" cols="12" >
          <v-subheader>Landscape settings</v-subheader>
          <p>There are no special settings to configure for Landscape at this time. Your commission bonuses will be applied automatically!</p>
        </v-col>
      </v-row>
      <v-row no-gutters   v-if="(subject.landscape)">
        <v-col class="text-center" cols="12" >
          <p>Your landscape subscription is paid through {{formatDate(subject.landscape_paid_through)}}.</p>
        </v-col>
        <v-col class="text-center" cols="12" sm="6" >
          <v-btn :to="{name: 'Payment', params: {username}}" color="primary">Update Payment Settings</v-btn>
        </v-col>
        <v-col class="text-center" cols="12" sm="6" v-if="subject.landscape_enabled">
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
        <v-col class="text-center" cols="12" sm="6" v-else-if="subject.landscape">
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
import {artCall} from '@/lib/lib'
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
}
</script>
