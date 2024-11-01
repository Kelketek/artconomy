<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink" :username="username">
    <template v-slot:title>
      <router-link :to="assetLink">{{event.target.username}} posted a Journal:</router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">{{event.data.journal.subject}}</router-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import {DisplayData, NotificationProps, NotificationUser, useEvent} from '../mixins/notification.ts'
import {computed} from 'vue'

import type {Journal} from '@/types/main'

declare interface NewJournal extends DisplayData {
  journal: Journal
}

const props = defineProps<NotificationProps<NotificationUser, NewJournal>>()
const event = useEvent(props)

const assetLink = computed(() => {
  return {
    name: 'Journal',
    params: {
      username: event.value.target.username,
      journalId: event.value.data.journal.id + '',
    },
  }
})
</script>

<style scoped>

</style>
