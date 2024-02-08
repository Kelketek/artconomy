<template>
  <ac-base-notification :notification="notification" :asset-link="characterLink">
    <template v-slot:title>
      <ac-link
          :to="characterLink">New Character: {{event.data.character.name}}
      </ac-link>
    </template>
    <template v-slot:subtitle>
      <ac-link
          :to="characterLink">By {{event.data.character.user.username}}
      </ac-link>
    </template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification.vue'
import Notifiction from '../mixins/notification.ts'
import AcLink from '@/components/wrappers/AcLink.vue'

export default {
  name: 'ac-new-character',
  components: {
    AcLink,
    AcBaseNotification,
  },
  mixins: [Notifiction],
  computed: {
    characterLink() {
      if (this.event.data.character) {
        return {
          name: 'Character',
          params: {
            username: this.event.data.character.user.username,
            characterName: this.event.data.character.name,
          },
        }
      }
      return null
    },
  },
}
</script>

<style scoped>

</style>
