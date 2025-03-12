<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="assetLink"
    :username="username"
  >
    <template #title>
      <router-link :to="assetLink">
        We had an issue sending money to your bank.
      </router-link>
    </template>
    <template #subtitle>
      <router-link :to="assetLink">
        Click here to change your bank settings.
      </router-link>
    </template>
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
import { User } from "@/store/profiles/types/main"

const props = defineProps<NotificationProps<User, DisplayUser>>()
const event = useEvent(props)

const assetLink = computed(() => {
  return {
    name: "Payout",
    params: {
      username: event.value.target.username,
    },
  }
})
</script>

<style scoped></style>
