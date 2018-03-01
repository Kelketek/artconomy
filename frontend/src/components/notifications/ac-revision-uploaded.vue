<template>
  <v-list-tile>
    <router-link :to="{name: 'Order', params: {orderID: event.target.id, username: viewer.username}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.revision, 'notification')" >
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <router-link :to="{name: 'Order', params: {orderID: event.target.id, username: viewer.username}}">
        <div class="pt-1 pb-1">
          <p><strong>A revision has been uploaded for Order #{{event.target.id}}</strong></p>
        </div>
      </router-link>
    </v-list-tile-content>
  </v-list-tile>
</template>

<style scoped>
</style>

<script>
  import AcAsset from '../ac-asset'
  import AcAction from '../ac-action'
  import Notification from '../../mixins/notification'

  export default {
    name: 'ac-revision-uploaded',
    components: {AcAsset, AcAction},
    mixins: [Notification],
    data () {
      return {}
    },
    computed: {
      url () {
        return `/api/sales/v1/order/${this.event.target.id}/`
      }
    }
  }
</script>