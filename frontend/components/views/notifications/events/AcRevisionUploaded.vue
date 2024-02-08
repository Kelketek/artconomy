<template>
  <ac-base-notification :asset-link="url" :notification="notification">
    <template v-slot:title>
      <router-link :to="url">
        Order #{{event.target.order.id}} [{{event.target.name}}]
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="url">A new revision has been added!</router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import Viewer from '@/mixins/viewer.ts'

export default {
  name: 'ac-revision-uploaded',
  components: {AcBaseNotification},
  mixins: [Notification, Viewer],
  data() {
    return {}
  },
  computed: {
    url() {
      if (this.event.target.revisions_hidden) {
        return {
          name: 'OrderDeliverableRevisions',
          params: {
            deliverableId: this.event.target.id,
            orderId: this.event.target.order.id,
            username: this.rawViewerName,
          },
        }
      }
      return {
        name: 'OrderDeliverableRevision',
        params: {
          deliverableId: this.event.target.id,
          orderId: this.event.target.order.id,
          username: this.rawViewerName,
          revisionId: this.event.data.revision.id,
        },
      }
    },
  },
}
</script>
