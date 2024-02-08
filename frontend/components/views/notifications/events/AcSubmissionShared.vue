<template>
  <ac-base-notification :asset-link="assetLink" :notification="notification">
    <template v-slot:title>
      <router-link :to="assetLink">
        A submission was shared with you
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">"{{event.data.submission.title}}" was shared by {{event.data.user.username}}
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification.ts'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'

export default {
  name: 'ac-submission-shared',
  components: {AcBaseNotification},
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    assetLink() {
      if (this.event.data.submission) {
        return {
          name: 'Submission',
          params: {submissionId: this.event.data.submission.id},
        }
      } else {
        return {}
      }
    },
  },
}
</script>

<style scoped>

</style>
