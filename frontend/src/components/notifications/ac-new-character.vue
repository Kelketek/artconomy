<template>
  <ac-base-notification :notification="notification" :asset-link="characterLink">
    <span slot="title"><router-link :to="characterLink">New Character: {{event.data.character.name}}</router-link></span>
    <span slot="subtitle"><router-link :to="characterLink">By {{event.data.character.user.username}}</router-link></span>
  </ac-base-notification>
</template>

<script>
  import AcBaseNotification from './ac-base-notification'
  import Notifiction from '../../mixins/notification'
  export default {
    name: 'ac-new-character',
    components: {AcBaseNotification},
    mixins: [Notifiction],
    computed: {
      characterLink () {
        if (this.event.data.character) {
          return {
            name: 'Character',
            params: {
              username: this.event.data.character.user.username, characterName: this.event.data.character.name
            }
          }
        }
      }
    }
  }
</script>

<style scoped>

</style>