<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="assetLink"
    :username="username"
  >
    <template #title>
      <router-link
        :to="assetLink"
      >
        Your waitlist has been updated. You now have {{ event.data.count }} orders on your waitlist.
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {
  DisplayData,
  NotificationProps,
  NotificationUser,
  useEvent,
} from '@/components/views/notifications/mixins/notification.ts'
import {computed} from 'vue'


declare interface WaitlistUpdated extends DisplayData<NotificationUser> {
  count: number,
}

const props = defineProps<NotificationProps<NotificationUser, WaitlistUpdated>>()
const event = useEvent(props)
const assetLink = computed(() => ({
  name: 'WaitingSales',
  params: {
    username: event.value.target.username,
  },
}))
</script>
