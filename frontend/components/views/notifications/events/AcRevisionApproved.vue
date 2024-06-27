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

<script setup lang="ts">
import {NotificationProps, useEvent} from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import {useViewer} from '@/mixins/viewer.ts'
import {computed} from 'vue'

const props = defineProps<NotificationProps<any, any>>()
const {rawViewerName} = useViewer()
const event = useEvent(props)

const url = computed(() => ({
  name: 'SaleDeliverableRevision',
  params: {
    deliverableId: event.value.data.deliverable.id,
    orderId: event.value.data.deliverable.order.id,
    username: rawViewerName.value,
    revisionId: event.value.target.id,
  },
}))

</script>
