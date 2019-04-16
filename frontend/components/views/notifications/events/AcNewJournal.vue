<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <span slot="title"><router-link :to="assetLink">{{event.target.username}} posted a Journal:</router-link></span>
    <span slot="subtitle"><router-link :to="assetLink">{{event.data.journal.subject}}</router-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'

export default {
  name: 'ac-new-journal',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      return {
        name: 'Journal',
        params: {
          username: this.event.target.username,
          journalID: this.event.data.journal.id + '',
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
