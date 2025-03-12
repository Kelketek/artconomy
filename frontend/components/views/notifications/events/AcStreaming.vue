<template>
  <ac-base-notification
    :notification="notification"
    :href-link="streamLink"
    :username="username"
  >
    <template #title>
      <a :href="streamLink" target="_blank"
        >{{ event.data.seller.username }} is streaming!</a
      >
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from "./AcBaseNotification.vue"
import {
  DisplayData,
  NotificationProps,
  NotificationUser,
  useEvent,
} from "../mixins/notification.ts"
import { computed } from "vue"
import type { Deliverable } from "@/types/main"

declare interface Streaming extends DisplayData {
  stream_link: string
  seller: NotificationUser
}
const props = defineProps<NotificationProps<Deliverable, Streaming>>()
const event = useEvent(props)

const streamLink = computed(() => {
  return event.value.data.stream_link || "#"
})
</script>

<style scoped></style>
