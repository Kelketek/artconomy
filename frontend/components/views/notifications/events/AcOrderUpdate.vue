<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink" :username="username">
    <template v-slot:title>
      <router-link :to="assetLink">Order #{{event.target.order.id}} [{{event.target.name}}]</router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">{{ message }}</router-link>
    </template>
    <template v-slot:extra>
      <v-list-item-subtitle>
        <a target="_blank" :href="streamingLink" v-if="streamingLink">Click here for stream!</a>
        <span v-if="autoFinalizeDisplay && event.target.auto_finalize_on">Will auto-finalize on {{formatDate(event.target.auto_finalize_on)}}.</span>
      </v-list-item-subtitle>
    </template>
  </ac-base-notification>
</template>

<style scoped>
</style>

<script setup lang="ts">
import {DisplayData, NotificationProps, useEvent} from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import {computed} from 'vue'
import {formatDate} from '@/lib/otherFormatters.ts'
import Deliverable from '@/types/Deliverable.ts'
import {DeliverableStatus, DeliverableStatusValue} from '@/types/DeliverableStatus.ts'

const ORDER_STATUSES: Record<DeliverableStatusValue, string> = {
  [DeliverableStatus.WAITING]: 'has been added to the artist\'s waitlist.',
  [DeliverableStatus.NEW]: 'has been placed, and is waiting for the artist to accept.',
  [DeliverableStatus.PAYMENT_PENDING]: 'requires payment to continue.',
  [DeliverableStatus.QUEUED]: 'has been added to the artist\'s queue!',
  [DeliverableStatus.IN_PROGRESS]: 'is currently in progress!',
  [DeliverableStatus.REVIEW]: 'is completed and awaiting for your review!',
  [DeliverableStatus.CANCELLED]: 'has been cancelled.',
  [DeliverableStatus.DISPUTED]: 'has been placed under dispute.',
  [DeliverableStatus.COMPLETED]: 'has been completed!',
  [DeliverableStatus.REFUNDED]: 'has been refunded.',
  [DeliverableStatus.LIMBO]: 'has been placed, and is waiting for the artist to accept.',
  [DeliverableStatus.MISSED]: 'has been cancelled.',
}

const props = defineProps<NotificationProps<Deliverable, DisplayData>>()
const event = useEvent(props)

const assetLink = computed(() => ({
  name: 'OrderDeliverableOverview',
  params: {
    orderId: event.value.target.order.id,
    username: props.username,
    deliverableId: event.value.target.id,
  },
}))

const message = computed(() => ORDER_STATUSES[event.value.target.status])
const streamingLink = computed(() => {
  if (event.value.target.status === 4) {
    return event.value.target.stream_link
  }
  return ''
})

const autoFinalizeDisplay = computed(() => event.value.target.status === 8)

</script>
