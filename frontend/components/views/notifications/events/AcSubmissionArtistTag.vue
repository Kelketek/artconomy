<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>An artist has been tagged on
      <router-link
          :to="assetLink">{{event.target.title}}!
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="{name: 'Profile', params: {username: userName}}">{{userName}}</router-link>
      tagged
      <router-link
          :to="{name: 'Profile', params: {username: artistName}}">{{artistName}}!
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification.vue'
import Notifiction from '../mixins/notification.ts'

export default {
  name: 'ac-submission-artist-tag',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      if (!this.event.target) {
        return
      }
      return {
        name: 'Submission',
        params: {assetID: this.event.target.id},
      }
    },
    userName() {
      return this.event.data.user.username
    },
    artistName() {
      return this.event.data.artist.username
    },
  },
}
</script>

<style scoped>

</style>
