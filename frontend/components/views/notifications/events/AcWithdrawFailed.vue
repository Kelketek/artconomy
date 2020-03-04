<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <span slot="title"><router-link :to="assetLink">We had an issue sending money to your bank.</router-link></span>
    <span slot="subtitle"><router-link :to="assetLink">Click here to change your bank settings.</router-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'

export default {
  name: 'ac-withdraw-failed',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      return {
        name: 'Payout',
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
