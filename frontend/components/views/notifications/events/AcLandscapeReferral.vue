<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="assetLink"
    :username="username"
  >
    <template #title>
      <router-link :to="assetLink">
        You've been credited for a referral!
      </router-link>
    </template>
    <template #subtitle>
      <router-link
        :to="assetLink"
      >
        You've received a month of Artconomy Landscape.
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
  name: 'LinksAndStats',
  params: {
    username: event.value.target.username,
  },
}))
</script>

<style scoped>

</style>
