<template>
  <v-list-item>
    <router-link :to="characterLink">
      <v-badge left overlap :model-value="!notification.read" color="primary">
        <template v-slot:badge>*</template>
        <template v-slot:prepend>
          <img :src="$img(event.data.display, 'notification', true)" alt="">
        </template>
      </v-badge>
    </router-link>
    <v-list-item-title>
      <router-link :to="characterLink">
        A character was shared with you
      </router-link>
    </v-list-item-title>
    <v-list-item-subtitle>
      <router-link :to="characterLink">"{{event.data.character.name}}" was shared by {{event.data.user.username}}
      </router-link>
    </v-list-item-subtitle>
  </v-list-item>
</template>

<script>
import Notification from '../mixins/notification.ts'

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
