<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      <router-link :to="assetLink">Order #{{event.target.order.id}} [{{event.target.name}}]</router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">{{ message }}</router-link>
    </template>
    <template v-slot:extra>
      <v-list-item-subtitle>
        <a target="_blank" :href="streamingLink" v-if="streamingLink">Click here for stream!</a>
        <span v-if="autofinalizeDisplay">Will autofinalize on {{formatDate(event.target.auto_finalize_on)}}.</span>
      </v-list-item-subtitle>
    </template>
  </ac-base-notification>
</template>

<style scoped>
</style>

<script>
import Notification from '../mixins/notification.ts'
import Formatting from '@/mixins/formatting.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'

const ORDER_STATUSES = {
  0: 'has been added to the artist\'s waitlist.',
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
  components: {AcBaseNotification},
  mixins: [Notification, Formatting],
  computed: {
    assetLink() {
      return {
        name: 'OrderDeliverableOverview',
        params: {
          orderId: this.event.target.order.id,
          username: this.viewer.username,
          deliverableId: this.event.target.id,
        },
      }
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
