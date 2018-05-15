<template>
  <v-container>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-inbox"><v-icon>mail</v-icon>&nbsp;Inbox</v-tab>
      <v-tab href="#tab-sent"><v-icon>send</v-icon>&nbsp;Sent</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-inbox">
        <ac-message-list :endpoint="`${url}inbox/`" :username="username" />
      </v-tab-item>
      <v-tab-item id="tab-sent">
        <ac-message-list :endpoint="`${url}sent/`" :username="username" />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
  import {paramHandleMap} from '../lib'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import AcMessageList from './ac-message-list'

  export default {
    name: 'Messages',
    components: {AcMessageList},
    mixins: [Viewer, Perms],
    computed: {
      tab: paramHandleMap('tabName', undefined, undefined, 'tab-inbox'),
      url () {
        return `/api/profiles/v1/account/${this.username}/messages/`
      }
    }
  }
</script>

<style scoped>

</style>