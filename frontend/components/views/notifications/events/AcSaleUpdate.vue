<template>
  <ac-base-notification
    :asset-link="assetLink"
    :notification="notification"
    :username="username"
  >
    <template #title>
      <router-link :to="assetLink">
        <span v-if="event.target.status === 10">New Order in Limbo</span>
        <span v-else-if="event.target.status === 11">Order expired.</span>
        <span v-else
          >Sale #{{ event.target.order.id }} [{{ event.target.name }}]</span
        >
      </router-link>
    </template>
    <template #subtitle>
      <router-link :to="assetLink">
        {{ message }}
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {
  DisplayData,
  NotificationProps,
  useEvent,
} from "../mixins/notification.ts"
import AcBaseNotification from "@/components/views/notifications/events/AcBaseNotification.vue"
import { DeliverableStatus } from "@/types/enums/DeliverableStatus.ts"
import { computed } from "vue"
import { useRouter } from "vue-router"
import type { Deliverable, DeliverableStatusValue } from "@/types/main"

const ORDER_STATUSES: Record<DeliverableStatusValue, string> = {
  [DeliverableStatus.WAITING]: "has been added to your waitlist.",
  [DeliverableStatus.NEW]: "has been placed, and is awaiting your acceptance!",
  [DeliverableStatus.PAYMENT_PENDING]: "is waiting on the commissioner to pay.",
  [DeliverableStatus.QUEUED]: "has been added to your queue.",
  [DeliverableStatus.IN_PROGRESS]:
    "is currently in progress. Update when you have a revision or the final completed.",
  [DeliverableStatus.REVIEW]:
    "is completed and awaiting the commissioner's review.",
  [DeliverableStatus.CANCELLED]: "has been cancelled.",
  [DeliverableStatus.DISPUTED]: "has been placed under dispute.",
  [DeliverableStatus.COMPLETED]: "has been completed!",
  [DeliverableStatus.REFUNDED]: "has been refunded.",
  [DeliverableStatus.LIMBO]: "Click here to upgrade and view your order!",
  [DeliverableStatus.MISSED]:
    "An order has expired. Upgrade to avoid this happening again!",
}

const props = defineProps<NotificationProps<Deliverable, DisplayData>>()
const router = useRouter()
const event = useEvent(props)

const assetLink = computed(() => {
  const deliverableLink = {
    name: "SaleDeliverableOverview",
    params: {
      orderId: event.value.target.order.id,
      username: props.username,
      deliverableId: event.value.target.id,
    },
  }
  if ([10, 11].includes(event.value.target.status)) {
    return {
      name: "Upgrade",
      params: { username: props.username },
      query: { next: router.resolve(deliverableLink).href },
    }
  }
  return deliverableLink
})

const message = computed(() => {
  return ORDER_STATUSES[event.value.target.status]
})
</script>

<style scoped>
.notification-asset img {
  max-width: 100%;
  max-height: 100%;
}
</style>
