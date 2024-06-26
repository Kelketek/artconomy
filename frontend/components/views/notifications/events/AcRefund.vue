<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink" :username="username">
    <template v-slot:title>
      <router-link :to="assetLink">Sale #{{event.target.id}} [{{event.target.name}}] was refunded. :(</router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {DisplayData, NotificationProps, useEvent} from '../mixins/notification.ts'
import Deliverable from '@/types/Deliverable.ts'
import {computed} from 'vue'

const props = defineProps<NotificationProps<Deliverable, DisplayData>>()
const event = useEvent(props)

const assetLink = computed(() => ({
  name: 'SaleDeliverableOverview',
  params: {
    username: event.value.target.order.seller.username,
    orderId: event.value.target.order.id,
    deliverableId: event.value.target.id,
  }
}))
</script>
