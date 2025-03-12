<template>
  <ac-base-notification :notification="notification" :username="username">
    <template #title>
      Your submission with ID {{ event.target.id }} was removed.
    </template>
    <template #subtitle> Reason: {{ reason }} </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from "./AcBaseNotification.vue"
import {
  NotificationProps,
  DisplayUser,
  useEvent,
} from "../mixins/notification.ts"
import { computed } from "vue"
import { Submission } from "@/types/main"
import { FLAGS_SHORT } from "@/lib/lib.ts"

const props =
  defineProps<
    NotificationProps<Submission, { comment: string } & DisplayUser>
  >()
const event = useEvent(props)
const reason = computed(() => FLAGS_SHORT[event.value.target.removed_reason!])
</script>

<style scoped></style>
