<template>
  <v-list-tile avatar>
    <router-link :to="{name: 'CharacterTransfer', params: {transferID: event.target.id, username: this.username}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.display, 'notification', true)" >
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <router-link :to="{name: 'CharacterTransfer', params: {transferID: event.target.id, username: this.username}}">
        <v-list-tile-title>Transfer for {{ characterName }}</v-list-tile-title>
      </router-link>
      <v-list-tile-sub-title>
        {{ message }}
      </v-list-tile-sub-title>
      <v-list-tile-sub-title v-if="streamingLink">
        <a target="_blank" :href="streamingLink">Click here for stream!</a>
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<script>
  import Notification from '../../mixins/notification'

  const STATUSES = {
    0: 'Awaiting approval',
    1: 'Transfer completed',
    2: 'Transfer cancelled',
    3: 'Transfer rejected'
  }
  export default {
    name: 'ac-char-transfer',
    mixins: [Notification],
    computed: {
      characterName () {
        if (this.event.target.character) {
          return this.event.target.character.name
        } else {
          return '<<Unknown>>'
        }
      },
      message () {
        return STATUSES[this.event.target.status]
      }
    }
  }
</script>

<style scoped>

</style>