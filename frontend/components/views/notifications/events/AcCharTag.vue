<template>
  <ac-base-notification :notification="notification" :asset-link="characterLink">
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

<script>
import Notification from '../mixins/notification.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'
import {profileLink} from '@/lib/lib.ts'

export default {
  name: 'ac-char-tag',
  components: {
    AcBaseNotification,
    AcLink,
  },
  mixins: [Notification],
  computed: {
    user() {
      return this.notification.event.data.user
    },
    userLink() {
      return profileLink(this.user)
    },
    submissionLink() {
      return {
        name: 'Submission',
        params: {submissionId: this.submission.id},
      }
    },
    submission() {
      return this.notification.event.data.submission
    },
    character() {
      return this.notification.event.data.character
    },
    characterLink() {
      return {
        name: 'Character',
        params: {
          username: this.character.user.username,
          characterName: this.character.name,
        },
      }
    },
  },
}
</script>
