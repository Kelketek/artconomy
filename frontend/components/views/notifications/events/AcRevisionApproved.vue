<template>
  <ac-base-notification :asset-link="url" :notification="notification">
    <template v-slot:title>
      <router-link :to="url">
        Sale #{{event.data.deliverable.order.id}} [{{event.data.deliverable.name}}]
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="url">Your revision/WIP has been approved!</router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification'
import Viewer from '@/mixins/viewer'

export default {
  name: 'ac-revision-approved',
  components: {AcBaseNotification},
  mixins: [Notification, Viewer],
  data() {
    return {}
  },
  computed: {
    url() {
      console.log(this.event)
      return {
        name: 'SaleDeliverableRevision',
        params: {
          deliverableId: this.event.data.deliverable.id,
          orderId: this.event.data.deliverable.order.id,
          username: this.rawViewerName,
          revisionId: this.event.target.id,
        },
      }
    },
  },
}
</script>
