<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="assetLink"
    :username="username"
  >
    <template #title>
      <router-link :to="assetLink">
        Sale #{{ event.target.id }} [{{ event.target.name }}] was refunded. :(
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from "./AcBaseNotification.vue"
import {
  DisplayData,
  NotificationProps,
  useEvent,
} from "../mixins/notification.ts"
import { computed } from "vue"
import type { Deliverable } from "@/types/main"

const props = defineProps<NotificationProps<Deliverable, DisplayData>>()
const event = useEvent(props)

const assetLink = computed(() => ({
  name: "SaleDeliverableOverview",
  params: {
    username: event.value.target.order.seller.username,
    orderId: event.value.target.order.id,
    deliverableId: event.value.target.id,
  },
}))
</script>
