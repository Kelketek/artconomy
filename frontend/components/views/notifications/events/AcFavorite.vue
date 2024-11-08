<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink" :username="username">
    <template v-slot:title>
      Your piece has been favorited!
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">{{event.target.title}}</router-link> has been favorited by
      <router-link :to="{name: 'Profile', params: {username: event.data.user.username}}">{{event.data.user.username}}!
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {DisplayData, NotificationProps, useEvent} from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import {computed} from 'vue'
import type {Submission} from '@/types/main'
import {TerseUser} from '@/store/profiles/types/main'

declare interface Favorite extends DisplayData {
  user: TerseUser,
}

const props = defineProps<NotificationProps<Submission, Favorite>>()
const event = useEvent(props)
const assetLink = computed(() => ({name: 'Submission', params: {'submissionId': event.value.target.id}}))
</script>
