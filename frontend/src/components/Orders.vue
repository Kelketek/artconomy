<template>
  <div class="container">
    <b-tabs v-model="tab">
      <b-tab title="<i class='fa fa-tasks'></i> Current">
        <ac-order-list :endpoint="`${url}current/`" :buyer="buyer" :username="username" />
      </b-tab>
      <b-tab title="<i class='fa fa-archive'></i> Archived">
        <ac-order-list :endpoint="`${url}archived/`" :buyer="buyer" :username="username" />
      </b-tab>
      <b-tab title="<i class='fa fa-ban'></i> Cancelled">
        <ac-order-list :endpoint="`${url}cancelled/`" :buyer="buyer" :username="username" />
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import AcOrderPreview from './ac-order-preview'
  import { paramHandleMap } from '../lib'
  import AcOrderList from './ac-order-list'

  const TabMap = {
    current: 0,
    archived: 1,
    cancelled: 2
  }

  export default {
    name: 'Orders',
    mixins: [Viewer, Perms],
    components: {
      AcOrderList,
      AcOrderPreview
    },
    props: ['url', 'buyer'],
    computed: {
      tab: paramHandleMap('tabName', TabMap)
    }
  }
</script>

<style scoped>

</style>