<template>
  <ac-base-notification :asset-link="url" :notification="notification">
    <router-link :to="url" slot="title">
      Sale #{{event.data.deliverable.order.id}} [{{event.data.deliverable.name}}]
    </router-link>
    <router-link :to="url" slot="subtitle">Your revision/WIP has been approved!</router-link>
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
