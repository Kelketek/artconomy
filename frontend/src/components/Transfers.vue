<template>
  <v-container>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-inbound" key="inbound">
        <v-icon>move_to_inbox</v-icon>&nbsp;Inbound
      </v-tab>
      <v-tab href="#tab-outbound" key="outbound">
        <v-icon>send</v-icon>&nbsp;Outbound
      </v-tab>
      <v-tab href="#tab-archived" key="archived">
        <v-icon>archive</v-icon>&nbsp;Archived
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item value="tab-inbound">
        <ac-character-transfer-list ref="charactersInbound" counter-name="characterInboundCount" class="pt-2" :endpoint="`/api/sales/v1/account/${username}/transfers/character/inbound/`" :username="username" />
      </v-tab-item>
      <v-tab-item value="tab-outbound">
        <ac-character-transfer-list ref="charactersOutbound" counter-name="characterOutboundCount" class="pt-2" :endpoint="`/api/sales/v1/account/${username}/transfers/character/outbound/`" :username="username" />
      </v-tab-item>
      <v-tab-item value="tab-archived">
        <ac-character-transfer-list ref="charactersArchive" counter-name="characterArchiveCount" class="pt-2" :endpoint="`/api/sales/v1/account/${username}/transfers/character/archive/`" :username="username" />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
  import {paramHandleMap} from '../lib'
  import Characters from './Characters'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import AcCharacterTransferList from './ac-character-transfer-list'

  export default {
    name: 'Transfers',
    mixins: [Viewer, Perms],
    components: {AcCharacterTransferList, Characters},
    computed: {
      tab: paramHandleMap('tabName', undefined, undefined, 'tab-inbound')
    }
  }
</script>

<style scoped>

</style>