<template>
  <v-list-tile avatar>
    <router-link :to="{name: 'Sale', params: {orderId: event.target.id, username: viewer.username}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.display, 'notification', true)" alt="">
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <v-list-tile-title>
        <router-link :to="{name: 'Sale', params: {orderId: event.target.id, username: viewer.username}}">
          Sale #{{event.target.id}}
        </router-link>
      </v-list-tile-title>
      <v-list-tile-sub-title>
        {{message}}
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<style scoped>
  .notification-asset img {
    max-width: 100%;
    max-height: 100%;
  }
</style>

<script>
import Notification from '../mixins/notification'

const ORDER_STATUSES = {
  1: 'has been placed, and is awaiting your acceptance!',
  2: 'is waiting on the commissioner to pay.',
  3: 'has been added to your queue.',
  4: 'is currently in progress. Update when you have a revision or the final completed.',
  5: 'is completed and awaiting the commissioner\'s review.',
  6: 'has been cancelled.',
  7: 'has been placed under dispute.',
  8: 'has been completed!',
  9: 'has been refunded.',
}

export default {
  name: 'ac-sale-update',
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    url() {
      return `/api/sales/v1/order/${this.event.target.id}/`
    },
    message() {
      return ORDER_STATUSES[this.event.target.status]
    },
    streamingLink() {
      if (this.event.target.status === 4) {
        return this.event.target.stream_link
      }
      return ''
    },
  },
}
</script>
