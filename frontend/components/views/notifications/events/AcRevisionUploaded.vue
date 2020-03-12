<template>
  <v-list-item>
    <router-link :to="{name: 'Order', params: {orderId: event.target.id, username: viewer.username}}">
      <v-badge left overlap :value="!notification.read">
        <span slot="badge">*</span>
        <v-avatar>
          <img :src="$img(event.data.revision, 'notification', true)" alt="">
        </v-avatar>
      </v-badge>
    </router-link>
    <v-list-item-content>
      <v-list-item-title>
        <router-link :to="{name: 'Order', params: {orderId: event.target.id, username: viewer.username}}">
          Order #{{event.target.id}}
        </router-link>
      </v-list-item-title>
      <v-list-item-subtitle>
        A new revision has been added!
      </v-list-item-subtitle>
    </v-list-item-content>
  </v-list-item>
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
