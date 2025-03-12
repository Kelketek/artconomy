<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="assetLink"
    :username="username"
  >
    <template #title>
      <router-link :to="assetLink">
        {{ buyerName }} sent you a tip!
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

import { deriveDisplayName } from "@/lib/otherFormatters.ts"
import { computed } from "vue"
import type { Deliverable } from "@/types/main"

const props = defineProps<NotificationProps<Deliverable, DisplayData>>()
const event = useEvent(props)

const assetLink = computed(() => {
  return {
    name: "SaleDeliverableOverview",
    params: {
      orderId: event.value.target.order.id,
      username: props.username,
      deliverableId: event.value.target.id,
    },
  }
})

const buyerName = computed(() => {
  return deriveDisplayName(event.value.target.order.buyer!.username)
})
</script>

<style scoped></style>
