<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="upgradeLink"
    :username="username"
  >
    <template #title>
      <router-link :to="upgradeLink">
        Your subscription has been deactivated.
      </router-link>
    </template>
    <template #subtitle>
      <router-link :to="upgradeLink">
        Click to upgrade your account again.
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {DisplayData, NotificationProps} from '@/components/views/notifications/mixins/notification.ts'
import {computed} from 'vue'

const props = defineProps<NotificationProps<null, DisplayData>>()
const upgradeLink = computed(() => {
  return {
    name: 'Upgrade',
    params: {
      username: props.username,
    }
  }
})
</script>

<style scoped>

</style>
