<template>
  <ac-base-notification :asset-link="assetLink" :notification="notification">
    <template v-slot:title>
      <router-link :to="assetLink">
        <span v-if="event.target.status === 10">New Order in Limbo</span>
        <span v-else>Sale #{{event.target.order.id}} [{{event.target.name}}]</span>
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">{{message}}</router-link>
    </template>
  </ac-base-notification>
</template>

<style scoped>
.notification-asset img {
  max-width: 100%;
  max-height: 100%;
}
</style>

<script>
import Notification from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'

const ORDER_STATUSES = {
  0: 'has been added to your waitlist.',
  1: 'has been placed, and is awaiting your acceptance!',
  2: 'is waiting on the commissioner to pay.',
  3: 'has been added to your queue.',
  4: 'is currently in progress. Update when you have a revision or the final completed.',
  5: 'is completed and awaiting the commissioner\'s review.',
  6: 'has been cancelled.',
  7: 'has been placed under dispute.',
  8: 'has been completed!',
  9: 'has been refunded.',
  10: 'Click here to upgrade and view your order!',
}

export default {
  name: 'ac-sale-update',
  components: {AcBaseNotification},
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    assetLink() {
      const deliverableLink = {
        name: 'SaleDeliverableOverview',
        params: {
          orderId: this.event.target.order.id,
          username: this.viewer.username,
          deliverableId: this.event.target.id,
        },
      }
      if (this.event.target.status === 10) {
        return {
          name: 'Upgrade',
          params: {username: this.viewer.username},
          query: {next: this.$router.resolve(deliverableLink).href},
        }
      }
      return deliverableLink
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
