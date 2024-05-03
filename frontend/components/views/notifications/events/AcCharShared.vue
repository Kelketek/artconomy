<template>
  <ac-base-notification :notification="notification" :asset-link="characterLink">
    <template v-slot:title>
      <ac-link :to="characterLink">
        A character was shared with you
      </ac-link>
    </template>
    <template v-slot:subtitle>
      <ac-link :to="characterLink">"{{event.data.character.name}}" was shared by {{event.data.user.username}}</ac-link>
    </template>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification.vue'

export default {
  name: 'ac-char-shared',
  components: {AcBaseNotification, AcLink},
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    characterLink() {
      if (this.event.data.character) {
        return {
          name: 'Character',
          params: {
            characterName: this.event.data.character.name,
            username: this.event.data.character.user.username,
          },
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
