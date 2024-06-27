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
import {useViewer} from '@/mixins/viewer.ts'
import {formatDate} from '@/lib/otherFormatters.ts'
import Deliverable from '@/types/Deliverable.ts'

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

const props = defineProps<NotificationProps<Deliverable, DisplayData>>()
const {viewer} = useViewer()
const event = useEvent(props)

const assetLink = computed(() => ({
  name: 'OrderDeliverableOverview',
  params: {
    orderId: event.value.target.order.id,
    username: viewer.value.username,
    deliverableId: event.value.target.id,
  },
}))

const message = computed(() => ORDER_STATUSES[event.value.target.status as keyof typeof ORDER_STATUSES])
const streamingLink = computed(() => {
  if (event.value.target.status === 4) {
    return event.value.target.stream_link
  }
  return ''
})

const autoFinalizeDisplay = computed(() => event.value.target.status === 8)

</script>
