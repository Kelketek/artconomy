<template>
  <ac-base-notification :asset-link="url" :notification="notification">
    <template v-slot:title>
      <router-link :to="url">
        Order #{{event.target.order.id}} [{{event.target.name}}]
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="url">A new reference has been added!</router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {DisplayData, NotificationProps, useEvent} from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import {useViewer} from '@/mixins/viewer.ts'
import Reference from '@/types/Reference.ts'
import Deliverable from '@/types/Deliverable.ts'
import {computed} from 'vue'

declare interface ReferenceUploaded extends DisplayData {
  reference: Reference,
}

const props = defineProps<NotificationProps<Deliverable, ReferenceUploaded>>()
const {rawViewerName} = useViewer()
const event = useEvent(props)

const url = computed(() => ({
  name: 'OrderDeliverableReference',
  params: {
    deliverableId: event.value.target.id,
    orderId: event.value.target.order.id,
    username: rawViewerName.value,
    referenceId: event.value.data.reference.id,
  },
}))
</script>
