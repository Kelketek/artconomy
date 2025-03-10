<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="characterLink"
    :username="username"
  >
    <template #title>
      <ac-link :to="characterLink">
        {{ character.name }}
      </ac-link>
      was tagged by
      <ac-link :to="userLink">
        {{ user.username }}
      </ac-link>
    </template>
    <template #subtitle>
      in
      <ac-link :to="submissionLink">
        "{{ submission.title }}"
      </ac-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {profileLink} from '@/lib/otherFormatters.ts'
import {
  DisplayData,
  NotificationProps,
  NotificationUser,
  useEvent,
} from '@/components/views/notifications/mixins/notification.ts'
import {computed} from 'vue'
import type {Submission} from '@/types/main'
import {Character} from '@/store/characters/types/main'

declare interface SubmissionCharTag extends DisplayData {
  user: NotificationUser,
  submission: Submission,
  character: Character,
}

const props = defineProps<NotificationProps<unknown, SubmissionCharTag>>()
const event = useEvent(props)
const user = computed(() => event.value.data.user)
const userLink = computed(() => profileLink(user.value))
const submission = computed(() => event.value.data.submission)
const submissionLink = computed(() => ({
  name: 'Submission',
  params: {submissionId: submission.value.id},
}))
const character = computed(() => event.value.data.character)
const characterLink = computed(() => ({
  name: 'Character',
  params: {
    username: character.value.user.username,
    characterName: character.value.name,
  },
}))
</script>
