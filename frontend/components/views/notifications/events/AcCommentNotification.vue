<template>
  <ac-base-notification :notification="notification" :asset-link="event.data.link">
    <template v-slot:title>
      <ac-link :to="event.data.link">{{titleText}}</ac-link>
    </template>
    <template v-slot:subtitle>
      <ac-link :to="event.data.link">{{byLine}}</ac-link>
    </template>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification.ts'
import AcBaseNotification from './AcBaseNotification.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {posse} from '@/lib/otherFormatters.ts'

export default {
  name: 'ac-comment-notification',
  components: {
    AcLink,
    AcBaseNotification,
  },
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    byLine() {
      let commenters = ''
      if (this.event.data.subject) {
        commenters += 'from '
      } else {
        commenters += 'by '
      }
      commenters += posse(this.event.data.commenters, this.event.data.additional)
      return commenters
    },
    titleText() {
      let message
      if (this.event.data.is_thread) {
        message = 'A comment has been added to a thread in '
      } else {
        message = 'A comment has been added in '
      }
      return message + this.event.data.name
    },
  },
}
</script>
