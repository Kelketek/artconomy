<template>
  <v-list-item>
    <router-link :to="{name: 'Submission', params: {'submissionId': event.target.id}}">
      <template v-slot:prepend>
        <img :src="$img(event.target, 'notification', true)" alt=""/>
      </template>
    </router-link>
    <v-list-item-title>
      Your piece has been favorited by
      <router-link :to="{name: 'Profile', params: {username: event.data.user.username}}">{{event.data.user.username}}!
      </router-link>
    </v-list-item-title>
  </v-list-item>
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
