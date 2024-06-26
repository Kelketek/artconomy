<template>
  <ac-base-notification :notification="notification" :asset-link="paymentLink" :username="username">
    <template v-slot:title>
      <router-link
          :to="paymentLink">There was an issue renewing your subscription.
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="paymentLink">The error we got was: {{event.data.error}}</router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {DisplayData, NotificationProps, NotificationUser, useEvent} from '../mixins/notification.ts'
import {computed} from 'vue'

declare interface RenewalFailure extends DisplayData {
  error: string,
}
const props = defineProps<NotificationProps<NotificationUser, RenewalFailure>>()
const event = useEvent(props)

const paymentLink = computed(() => ({
  name: 'Settings',
  params: {
    username: event.value.target.username,
    tabName: 'payment',
  },
}))
</script>

<style scoped>

</style>
