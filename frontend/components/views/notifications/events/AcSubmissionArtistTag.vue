<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink" :username="username">
    <template v-slot:title>An artist has been tagged on
      <router-link
          :to="assetLink">{{event.target.title}}!
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="{name: 'Profile', params: {username: userName}}">{{userName}}</router-link>
      tagged
      <router-link
          :to="{name: 'Profile', params: {username: artistName}}">{{artistName}}!
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {DisplayData, NotificationProps, NotificationUser, useEvent} from '../mixins/notification.ts'
import {computed} from 'vue'

import type {Submission} from '@/types/main'

declare interface SubmissionArtistTag extends DisplayData<Submission> {
  user: NotificationUser,
  artist: NotificationUser,
}

const props = defineProps<NotificationProps<Submission, SubmissionArtistTag>>()
const event = useEvent(props)

const assetLink = computed(() => ({
  name: 'Submission',
  params: {assetID: event.value.target.id},
}))

const userName = computed(() => event.value.data.user.username)
const artistName = computed(() => event.value.data.artist.username)
</script>

<style scoped>

</style>
