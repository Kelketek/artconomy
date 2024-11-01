<template>
  <ac-base-notification :asset-link="url" :notification="notification" :username="username">
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
import {computed} from 'vue'
import type {Deliverable, Reference} from '@/types/main'

declare interface ReferenceUploaded extends DisplayData {
  reference: Reference,
}

const props = defineProps<NotificationProps<Deliverable, ReferenceUploaded>>()
const event = useEvent(props)

const url = computed(() => ({
  name: 'OrderDeliverableReference',
  params: {
    deliverableId: event.value.target.id,
    orderId: event.value.target.order.id,
    username: props.username,
    referenceId: event.value.data.reference.id,
  },
}))
</script>
