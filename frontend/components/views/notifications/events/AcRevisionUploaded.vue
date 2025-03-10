<template>
  <ac-base-notification
    :asset-link="url"
    :notification="notification"
    :username="username"
  >
    <template #title>
      <router-link :to="url">
        Order #{{ event.target.order.id }} [{{ event.target.name }}]
      </router-link>
    </template>
    <template #subtitle>
      <router-link :to="url">
        A new revision has been added!
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {DisplayData, NotificationProps, useEvent} from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import {computed} from 'vue'
import type {Deliverable, Revision} from '@/types/main'

declare interface RevisionUploaded extends DisplayData {
  revision?: Revision
}

const props = defineProps<NotificationProps<Deliverable, RevisionUploaded>>()
const event = useEvent(props)

const url = computed(() => {
  if (event.value.data.revision) {
    return {
      name: 'OrderDeliverableRevision',
      params: {
        deliverableId: event.value.target.id,
        orderId: event.value.target.order.id,
        username: props.username,
        revisionId: event.value.data.revision.id,
      },
    }
  }
  return {
    name: 'OrderDeliverableRevisions',
    params: {
      deliverableId: event.value.target.id,
      orderId: event.value.target.order.id,
      username: props.username,
    },
  }
})
</script>
