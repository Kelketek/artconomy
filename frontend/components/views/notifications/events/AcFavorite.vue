<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      Your piece <router-link :to="assetLink">{{event.target.title}}</router-link> has been favorited by
      <router-link :to="{name: 'Profile', params: {username: event.data.user.username}}">{{event.data.user.username}}!
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'

export default {
  name: 'ac-favorite',
  components: {AcBaseNotification},
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    assetLink() {
      return {name: 'Submission', params: {'submissionId': this.event.target.id}}
    }
  }
}
</script>
