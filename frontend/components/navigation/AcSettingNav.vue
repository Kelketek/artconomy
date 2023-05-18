<!--suppress XmlUnboundNsPrefix -->
<template>
  <v-list v-if="subject" no-action>
    <v-list-item :to="{name: 'Options', params: {username}}" exact>
      <v-list-item-title>Options</v-list-item-title>
      <v-list-item-icon>
        <v-icon>build</v-icon>
      </v-list-item-icon>
    </v-list-item>
    <v-list-item class="artist-panel-link" :to="{name: 'Artist', params: {username}}" exact v-if="subject.artist_mode">
      <v-list-item-title>Artist</v-list-item-title>
      <v-list-item-icon>
        <v-icon>palette</v-icon>
      </v-list-item-icon>
    </v-list-item>
    <v-list-item :to="{name: 'Email', params: {username}}" exact>
      <v-list-item-title>Email Notifications</v-list-item-title>
      <v-list-item-icon>
        <v-icon>send</v-icon>
      </v-list-item-icon>
    </v-list-item>
    <v-list-item :to="{name: 'Login Details', params: {username}}">
      <v-list-item-title>Login Details</v-list-item-title>
      <v-list-item-icon>
        <v-icon>lock</v-icon>
      </v-list-item-icon>
    </v-list-item>
    <v-list-item :to="{name: 'Avatar', params: {username}}">
      <v-list-item-title>Avatar</v-list-item-title>
      <v-list-item-icon>
        <v-icon>person</v-icon>
      </v-list-item-icon>
    </v-list-item>
    <v-list-item :to="{name: 'Premium', params: {username}}">
      <v-list-item-title>Premium</v-list-item-title>
      <v-list-item-icon>
        <v-icon>star</v-icon>
      </v-list-item-icon>
    </v-list-item>
    <v-list-group
        no-action :value="true"
        sub-group
        append-icon="attach_money"
    >
      <template v-slot:activator>
        <v-list-item-title>Payment</v-list-item-title>
      </template>
      <v-list-item :to="{name: 'Purchase', params: {username}}">
        <v-list-item-action>
          <v-icon>credit_card</v-icon>
        </v-list-item-action>
        <v-list-item-title>Payment Methods</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Payout', params: {username}}" class="payout-link" v-if="showPayout">
        <v-list-item-action>
          <v-icon>account_balance_wallet</v-icon>
        </v-list-item-action>
        <v-list-item-title>Payout Methods</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Invoices', params: {username}}">
        <v-list-item-action>
          <v-icon>receipt</v-icon>
        </v-list-item-action>
        <v-list-item-title>Invoices</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'TransactionHistory', params: {username}}">
        <v-list-item-action>
          <v-icon>list</v-icon>
        </v-list-item-action>
        <v-list-item-title>Raw Transaction History</v-list-item-title>
      </v-list-item>
    </v-list-group>
  </v-list>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '../../mixins/viewer'
import Subjective from '../../mixins/subjective'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'
import {User} from '@/store/profiles/types/User'
import {Prop} from 'vue-property-decorator'
import * as VListComponents from 'vuetify/es5/components/VList'

@Component({
  components: {
    ...VListComponents,
  },
})
export default class AcSettingNav extends mixins(Viewer, Subjective) {
  @Prop({default: false})
  public nested!: boolean

  public HAS_US_ACCOUNT = 1 as BANK_STATUSES

  public get hasUSAccount() {
    const profile = this.subjectHandler.artistProfile
    return profile.x && (profile.x.bank_account_status === this.HAS_US_ACCOUNT)
  }

  public get showPayout() {
    const subject = this.subject as User
    return subject.artist_mode || this.hasUSAccount
  }

  public created() {
    this.subjectHandler.artistProfile.get().then()
  }
}
</script>
