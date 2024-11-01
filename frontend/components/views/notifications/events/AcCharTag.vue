<template>
  <ac-base-notification :notification="notification" :asset-link="characterLink" :username="username">
    <template v-slot:title>
      <ac-link :to="characterLink">{{ character.name }}</ac-link>
      was tagged by
      <ac-link :to="userLink">{{user.username}}</ac-link>
    </template>
    <template v-slot:subtitle>in
      <ac-link :to="submissionLink">"{{submission.title}}"</ac-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {DisplayData, NotificationProps, useEvent} from '../mixins/notification.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import {profileLink} from '@/lib/otherFormatters.ts'
import {computed} from 'vue'
import type {Submission} from '@/types/main'
import {TerseUser} from '@/store/profiles/types/main'
import {Character} from '@/store/characters/types/main'

declare interface CharTag extends DisplayData {
  submission: Submission,
  character: Character,
  user: TerseUser,
}
const props = defineProps<NotificationProps<Character, CharTag>>()
const event = useEvent(props)

const user = computed(() => event.value.data.user)
const userLink = computed(() => profileLink(user.value))
const submission = computed(() => event.value.data.submission)
const character = computed(() => event.value.data.character)
const submissionLink = computed(() => ({
  name: 'Submission',
  params: {submissionId: submission.value.id},
}))
const characterLink = computed(() => {
  return {
    name: 'Character',
    params: {
      username: character.value.user.username,
      characterName: character.value.name,
    },
  }
})
</script>
