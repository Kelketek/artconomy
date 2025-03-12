<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="casePath"
    :username="username"
  >
    <template #title>
      A Dispute has been filed for Deliverable #{{ event.target.id }}.
    </template>
    <template #extra>
      <v-btn variant="flat" small @click="claimDispute"> Claim </v-btn>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {
  DisplayData,
  NotificationProps,
  useEvent,
} from "../mixins/notification.ts"
import { artCall } from "@/lib/lib.ts"
import { useRouter } from "vue-router"
import { computed } from "vue"
import AcBaseNotification from "@/components/views/notifications/events/AcBaseNotification.vue"
import type { Deliverable } from "@/types/main"

const props = defineProps<NotificationProps<Deliverable, DisplayData>>()
const event = useEvent(props)

const router = useRouter()
const url = computed(() => {
  return `/api/sales/order/${event.value.target.order.id}/deliverables/${event.value.target.id}/`
})
const casePath = computed(() => {
  return {
    name: "CaseDeliverableOverview",
    params: {
      orderId: event.value.target.order.id,
      username: props.username,
      deliverableId: event.value.target.id,
    },
  }
})
const visitOrder = () => router.push(casePath.value)
const claimDispute = () => {
  artCall({
    url: `${url.value}claim/`,
    method: "post",
  }).then(visitOrder)
}
</script>

<style scoped></style>
