<template>
  <v-list-tile avatar>
    <router-link :to="{name: 'Submission', params: {'submissionId': event.target.id}}">
      <v-list-tile-avatar>
        <img :src="$img(event.target, 'notification', true)" alt=""/>
      </v-list-tile-avatar>
    </router-link>
    <v-list-tile-title>
      Your piece has been favorited by
      <router-link :to="{name: 'Profile', params: {username: event.data.user.username}}">{{event.data.user.username}}!
      </router-link>
    </v-list-tile-title>
  </v-list-tile>
</template>

<script>
import Notification from '../mixins/notification'

export default {
  name: 'ac-favorite',
  mixins: [Notification],
  data() {
    return {}
  },
}
</script>
