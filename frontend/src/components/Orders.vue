<template>
  <div>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-current" key="current">
        <v-icon>list</v-icon>&nbsp;Current
      </v-tab>
      <v-tab href="#tab-archived" key="archived">
        <v-icon>archive</v-icon>&nbsp;Archived
      </v-tab>
      <v-tab href="#tab-cancelled" key="cancelled">
        <v-icon>do_not_disturb</v-icon>&nbsp;Cancelled
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-current">
        <ac-order-list :url="`${url}current/`" :buyer="buyer" :username="username" />
      </v-tab-item>
      <v-tab-item id="tab-archived">
        <ac-order-list :url="`${url}archived/`" :buyer="buyer" :username="username" />
      </v-tab-item>
      <v-tab-item id="tab-cancelled">
        <ac-order-list :url="`${url}cancelled/`" :buyer="buyer" :username="username" />
      </v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import AcOrderPreview from './ac-order-preview'
  import { paramHandleMap } from '../lib'
  import AcOrderList from './ac-order-list'

  export default {
    name: 'Orders',
    mixins: [Viewer, Perms],
    components: {
      AcOrderList,
      AcOrderPreview
    },
    data () {
      return {
        // Used by tab mapper
        query: null
      }
    },
    props: ['url', 'buyer'],
    computed: {
      tab: paramHandleMap('tabName', undefined, undefined, 'tab-current')
    }
  }
</script>

<style scoped>

</style>