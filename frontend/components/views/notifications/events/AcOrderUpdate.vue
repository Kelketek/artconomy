<template>
  <v-list-tile avatar>
    <router-link :to="{name: 'Order', params: {orderId: event.target.id, username: viewer.username}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.display, 'notification', true)" alt="">
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <router-link :to="{name: 'Order', params: {orderId: event.target.id, username: viewer.username}}">
        <v-list-tile-title>Order #{{event.target.id}}</v-list-tile-title>
      </router-link>
      <v-list-tile-sub-title>
        {{ message }}
      </v-list-tile-sub-title>
      <v-list-tile-sub-title>
        <a target="_blank" :href="streamingLink" v-if="streamingLink">Click here for stream!</a>
        <span v-if="autofinalizeDisplay">Will autofinalize on {{formatDate(event.target.auto_finalize_on)}}.</span>
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<style scoped>
</style>

<script>
import Notification from '../mixins/notification'
import Formatting from '../../../../mixins/formatting'

const ORDER_STATUSES = {
  1: 'has been placed, and is waiting for the artist to accept.',
  2: 'requires payment to continue.',
  3: 'has been added to the artist\'s queue!',
  4: 'is currently in progress!',
  5: 'is completed and awaiting for your review!',
  6: 'has been cancelled.',
  7: 'has been placed under dispute.',
  8: 'has been completed!',
  9: 'has been refunded.',
}

export default {
  name: 'ac-order-update',
  mixins: [Notification, Formatting],
  computed: {
    url() {
      return `/api/sales/v1/order/${this.event.target.id}/`
    },
    message() {
      return ORDER_STATUSES[this.event.target.status + '']
    },
    streamingLink() {
      if (this.event.target.status === 4) {
        return this.event.target.stream_link
      }
      return ''
    },
    autofinalizeDisplay() {
      return this.event.target.status === '8'
    },
  },
}
</script>
