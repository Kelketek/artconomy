<!--suppress XmlUnboundNsPrefix -->
<template>
  <v-list v-if="subject">
    <v-list-tile :to="{name: 'Options', params: {username}}" exact>
      <v-list-tile-action>
        <v-icon>build</v-icon>
      </v-list-tile-action>
      <v-list-tile-title>Options</v-list-tile-title>
    </v-list-tile>
    <v-list-tile class="artist-panel-link" :to="{name: 'Artist', params: {username}}" exact v-if="subject.artist_mode">
      <v-list-tile-action>
        <v-icon>palette</v-icon>
      </v-list-tile-action>
      <v-list-tile-title>Artist</v-list-tile-title>
    </v-list-tile>
    <v-list-tile :to="{name: 'Credentials', params: {username}}">
      <v-list-tile-action>
        <v-icon>lock</v-icon>
      </v-list-tile-action>
      <v-list-tile-title>Credentials</v-list-tile-title>
    </v-list-tile>
    <v-list-tile :to="{name: 'Avatar', params: {username}}">
      <v-list-tile-action>
        <v-icon>person</v-icon>
      </v-list-tile-action>
      <v-list-tile-title>Avatar</v-list-tile-title>
    </v-list-tile>
    <v-list-tile :to="{name: 'Premium', params: {username}}">
      <v-list-tile-action>
        <v-icon>star</v-icon>
      </v-list-tile-action>
      <v-list-tile-title>Premium</v-list-tile-title>
    </v-list-tile>
    <v-list-group
        no-action :value="true"
    >
      <template v-slot:activator>
        <v-list-tile>
          <v-list-tile-action>
            <v-icon>attach_money</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Payment</v-list-tile-title>
        </v-list-tile>
      </template>
      <v-list-tile :to="{name: 'Purchase', params: {username}}">
        <v-list-tile-action>
          <v-icon>credit_card</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Payment Methods</v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'Payout', params: {username}}" class="payout-link" v-if="showPayout">
        <v-list-tile-action>
          <v-icon>account_balance_wallet</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Payout Methods</v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'TransactionHistory', params: {username}}">
        <v-list-tile-action>
          <v-icon>list</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Transaction History</v-list-tile-title>
      </v-list-tile>
    </v-list-group>
  </v-list>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '../../mixins/viewer'
import Subjective from '../../mixins/subjective'
import {BankStatus} from '@/store/profiles/types/BankStatus'
import {User} from '@/store/profiles/types/User'

  @Component
export default class AcSettingNav extends mixins(Viewer, Subjective) {
    public HAS_US_ACCOUNT = 1 as BankStatus

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
