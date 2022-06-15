<template>
  <ac-base-notification :notification="notification" :asset-link="characterLink">
    <span slot="title"><ac-link :to="characterLink">{{ character.name }}</ac-link> was tagged by <ac-link :to="userLink">{{user.username}}</ac-link></span>
    <span slot="subtitle">in <ac-link :to="submissionLink">"{{submission.title}}"</ac-link></span>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification'
import AcLink from '@/components/wrappers/AcLink'
import {profileLink} from '@/lib/lib'

export default {
  name: 'ac-submission-char-tag',
  components: {AcLink, AcBaseNotification},
  mixins: [Notification],
  computed: {
    user() {
      return this.notification.event.data.user
    },
    userLink() {
      return profileLink(this.user)
    },
    submissionLink() {
      return {name: 'Submission', params: {submissionId: this.submission.id}}
    },
    submission() {
      return this.notification.event.data.submission
    },
    character() {
      return this.notification.event.data.character
    },
    characterLink() {
      return {name: 'Character', params: {username: this.character.user.username, characterName: this.character.name}}
    }
  }
}
</script>
