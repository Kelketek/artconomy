<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="transactionLink"
    :username="username"
  >
    <template #title>
      <router-link
        :to="transactionLink"
      >
        Your subscription has renewed successfully!
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

const props = defineProps<NotificationProps<NotificationUser, DisplayData>>()
const event = useEvent(props)

const transactionLink = computed(() => ({
  name: 'Settings',
  params: {
    username: event.value.target.username,
    tabName: 'payment',
    subTabName: 'transactions',
    tertiaryTabName: 'purchases',
  },
}))
</script>

<style scoped>

</style>
