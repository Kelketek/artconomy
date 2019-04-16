<template>
  <v-list-tile avatar>
    <router-link :to="{name: 'Order', params: {orderId: event.target.id, username: viewer.username}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.revision, 'notification', true)" alt="">
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <v-list-tile-title>
        <router-link :to="{name: 'Order', params: {orderId: event.target.id, username: viewer.username}}">
          Order #{{event.target.id}}
        </router-link>
      </v-list-tile-title>
      <v-list-tile-sub-title>
        A new revision has been added!
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<script>
import Notification from '../mixins/notification'

export default {
  name: 'ac-revision-uploaded',
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    url() {
      return `/api/sales/v1/order/${this.event.target.id}/`
    },
  },
}
</script>
