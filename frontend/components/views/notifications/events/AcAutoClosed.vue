<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      <router-link :to="assetLink">Your sales have been automatically closed for inactivity.</router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {DisplayData, NotificationProps} from '../mixins/notification.ts'
import {computed} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'

const props = defineProps<NotificationProps<null, DisplayData>>()
const {viewer} = useViewer()
const assetLink = computed(() => ({
  name: 'Sales',
  params: {
    username: viewer.value.username,
  },
}))
</script>

<style scoped>

</style>
