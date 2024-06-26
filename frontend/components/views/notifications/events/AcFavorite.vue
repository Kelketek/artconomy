<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink" :username="username">
    <template v-slot:title>
      Your piece <router-link :to="assetLink">{{event.target.title}}</router-link> has been favorited by
      <router-link :to="{name: 'Profile', params: {username: event.data.user.username}}">{{event.data.user.username}}!
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {DisplayData, NotificationProps, useEvent} from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import {computed} from 'vue'
import Submission from '@/types/Submission.ts'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'

declare interface Favorite extends DisplayData {
  user: TerseUser,
}

const props = defineProps<NotificationProps<Submission, Favorite>>()
const event = useEvent(props)
const assetLink = computed(() => ({name: 'Submission', params: {'submissionId': event.value.target.id}}))
</script>
