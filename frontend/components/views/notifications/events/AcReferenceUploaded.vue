<template>
  <ac-base-notification :asset-link="url" :notification="notification">
    <template v-slot:title>
      <router-link :to="url" slot="title">
        Order #{{event.target.order.id}} [{{event.target.name}}]
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="url">A new reference has been added!</router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification'
import Viewer from '@/mixins/viewer'

export default {
  name: 'ac-reference-uploaded',
  components: {AcBaseNotification},
  mixins: [Notification, Viewer],
  data() {
    return {}
  },
  computed: {
    url() {
      return {
        name: 'OrderDeliverableReference',
        params: {
          deliverableId: this.event.target.id,
          orderId: this.event.target.order.id,
          username: this.rawViewerName,
          referenceId: this.event.data.reference.id,
        },
      }
    },
  },
}
</script>
