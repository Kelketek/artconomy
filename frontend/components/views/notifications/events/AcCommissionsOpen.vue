<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="assetLink"
    :username="username"
  >
    <template #title>
      <router-link :to="assetLink">
        {{ event.target.username }} is open!
      </router-link>
    </template>
    <template #subtitle>
      <router-link :to="assetLink">
        Click here to commission them.
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {DisplayData, NotificationProps, NotificationUser, useEvent} from '../mixins/notification.ts'
import {computed} from 'vue'

import {TerseUser} from '@/store/profiles/types/main'

const props = defineProps<NotificationProps<TerseUser, DisplayData<NotificationUser>>>()
const event = useEvent(props)

const assetLink = computed(() => ({
  name: 'Profile',
  params: {
    username: event.value.target.username,
    tabName: 'products',
  },
}))
</script>

<style scoped>

</style>
