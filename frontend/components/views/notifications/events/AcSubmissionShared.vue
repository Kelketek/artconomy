<template>
  <ac-base-notification
    :asset-link="assetLink"
    :notification="notification"
    :username="username"
  >
    <template #title>
      <router-link :to="assetLink">
        A submission was shared with you
      </router-link>
    </template>
    <template #subtitle>
      <router-link :to="assetLink">
        "{{ event.data.submission.title }}" was shared by
        {{ event.data.user.username }}
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {
  DisplayData,
  NotificationProps,
  NotificationUser,
  useEvent,
} from "../mixins/notification.ts"
import AcBaseNotification from "@/components/views/notifications/events/AcBaseNotification.vue"
import { computed } from "vue"
import type { Submission } from "@/types/main"

declare interface SubmissionShared extends DisplayData {
  user: NotificationUser
  submission: Submission
}

const props = defineProps<NotificationProps<null, SubmissionShared>>()
const event = useEvent(props)

const assetLink = computed(() => {
  if (event.value.data.submission) {
    return {
      name: "Submission",
      params: { submissionId: event.value.data.submission.id },
    }
  } else {
    return {}
  }
})
</script>

<style scoped></style>
