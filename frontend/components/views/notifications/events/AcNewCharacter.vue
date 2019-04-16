<template>
  <ac-base-notification :notification="notification" :asset-link="characterLink">
    <span slot="title"><ac-link
        :to="characterLink">New Character: {{event.data.character.name}}</ac-link></span>
    <span slot="subtitle"><ac-link
        :to="characterLink">By {{event.data.character.user.username}}</ac-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'
import AcLink from '@/components/wrappers/AcLink'

export default {
  name: 'ac-new-character',
  components: {AcLink, AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    characterLink() {
      if (this.event.data.character) {
        return {
          name: 'Character',
          params: {
            username: this.event.data.character.user.username, characterName: this.event.data.character.name,
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
