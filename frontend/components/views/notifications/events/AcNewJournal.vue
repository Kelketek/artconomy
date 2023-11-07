<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      <router-link :to="assetLink">{{event.target.username}} posted a Journal:</router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">{{event.data.journal.subject}}</router-link>
    </template>
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
          journalId: this.event.data.journal.id + '',
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
