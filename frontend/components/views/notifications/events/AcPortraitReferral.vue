<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <span slot="title"><router-link :to="assetLink">You've been credited for a referral!</router-link></span>
    <span slot="subtitle"><router-link
        :to="assetLink">You've received a month of Artconomy Portrait.</router-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'

export default {
  name: 'ac-portrait-referral',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      return {
        name: 'LinksAndStats',
        params: {
          username: this.event.target.username,
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
