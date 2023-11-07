<!--suppress XmlUnboundNsPrefix -->
<template>
  <v-list v-if="subject" no-action v-model:opened="open" nav density="compact">
    <v-list-item :to="{name: 'Options', params: {username}}" exact>
      <v-list-item-title>Options</v-list-item-title>
      <template v-slot:append>
        <v-icon icon="mdi-wrench"/>
      </template>
    </v-list-item>
    <v-list-item class="artist-panel-link" :to="{name: 'Artist', params: {username}}" exact v-if="subject.artist_mode">
      <v-list-item-title>Artist</v-list-item-title>
      <template v-slot:append>
        <v-icon icon="mdi-palette"/>
      </template>
    </v-list-item>
    <v-list-item :to="{name: 'Email', params: {username}}" exact>
      <v-list-item-title>Email Notifications</v-list-item-title>
      <template v-slot:append>
        <v-icon icon="mdi-send"/>
      </template>
    </v-list-item>
    <v-list-item :to="{name: 'Login Details', params: {username}}">
      <v-list-item-title>Login Details</v-list-item-title>
      <template v-slot:append>
        <v-icon icon="mdi-lock"/>
      </template>
    </v-list-item>
    <v-list-item :to="{name: 'Avatar', params: {username}}">
      <v-list-item-title>Avatar</v-list-item-title>
      <template v-slot:append>
        <v-icon icon="mdi-account"/>
      </template>
    </v-list-item>
    <v-list-item :to="{name: 'Premium', params: {username}}">
      <v-list-item-title>Premium</v-list-item-title>
      <template v-slot:append>
        <v-icon icon="mdi-star"/>
      </template>
    </v-list-item>
    <v-list-group
        value="Payment"
        density="compact"
    >
      <template v-slot:activator="{props}">
        <v-list-item v-bind="props">
          <v-list-item-title>Payment</v-list-item-title>
        </v-list-item>
      </template>
      <v-list-item :to="{name: 'Purchase', params: {username}}">
        <template v-slot:append>
          <v-icon icon="mdi-credit-card"/>
        </template>
        <v-list-item-title>Payment Methods</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Payout', params: {username}}" class="payout-link" v-if="showPayout">
        <template v-slot:append>
          <v-icon icon="mdi-wallet"/>
        </template>
        <v-list-item-title>Payout Methods</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Invoices', params: {username}}">
        <template v-slot:append>
          <v-icon icon="mdi-receipt-text"/>
        </template>
        <v-list-item-title>Invoices</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'TransactionHistory', params: {username}}">
        <template v-slot:append>
          <v-icon icon="mdi-list-box"/>
        </template>
        <v-list-item-title>Raw Transaction History</v-list-item-title>
      </v-list-item>
    </v-list-group>
  </v-list>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Viewer from '../../mixins/viewer'
import Subjective from '../../mixins/subjective'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'
import {User} from '@/store/profiles/types/User'
// import {VList, VListItem, VListItemAction, VListItemTitle, VListGroup, VListImg} from 'vuetify/lib/components/VList/index.mjs'
import * as VListComponents from 'vuetify/lib/components/VList/index.mjs'

@Component({
  components: {
    ...VListComponents,
  },
})
class AcSettingNav extends mixins(Viewer, Subjective) {
  @Prop({default: false})
  public nested!: boolean

  public open = ['Payment']

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

export default toNative(AcSettingNav)
</script>
