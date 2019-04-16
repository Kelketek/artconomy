<template>
  <ac-base-notification :notification="notification" :asset-link="event.data.link">
    <span slot="title"><router-link :to="event.data.link">{{titleText}}</router-link></span>
    <span slot="subtitle"><router-link :to="event.data.link">{{byLine}}</router-link></span>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification'
import AcBaseNotification from './AcBaseNotification'
import {posse} from '../../../../lib'

export default {
  name: 'ac-comment-notification',
  components: {AcBaseNotification},
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
