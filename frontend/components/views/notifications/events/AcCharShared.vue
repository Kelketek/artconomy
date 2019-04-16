<template>
  <v-list-tile avatar>
    <router-link :to="characterLink">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.display, 'notification', true)">
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <v-list-tile-title>
        <router-link :to="characterLink">
          A character was shared with you
        </router-link>
      </v-list-tile-title>
      <v-list-tile-sub-title>
        <router-link :to="characterLink">"{{event.data.character.name}}" was shared by {{event.data.user.username}}
        </router-link>
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<script>
import Notification from '../mixins/notification'

export default {
  name: 'ac-char-shared',
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
            characterName: this.event.data.character.name, username: this.event.data.character.user.username,
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
