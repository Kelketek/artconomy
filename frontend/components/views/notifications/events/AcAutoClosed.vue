<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink" :username="username">
    <template v-slot:title>
      <router-link :to="assetLink">Your sales have been automatically closed for inactivity.</router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {DisplayData, NotificationProps} from '../mixins/notification.ts'
import {computed} from 'vue'

const props = defineProps<NotificationProps<null, DisplayData>>()
const assetLink = computed(() => ({
  name: 'Sales',
  params: {
    username: props.username,
  },
}))
</script>

<style scoped>

</style>
