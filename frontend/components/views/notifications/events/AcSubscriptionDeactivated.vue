<template>
  <ac-base-notification :notification="notification" :asset-link="upgradeLink">
    <span slot="title"><router-link :to="upgradeLink">Your subscription has been deactivated.</router-link></span>
    <span slot="subtitle"><router-link :to="upgradeLink">Click to upgrade your account again.</router-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'

export default {
  name: 'ac-subscription-deactivated',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    upgradeLink() {
      return {
        name: 'Upgrade',
      }
    },
  },
}
</script>

<style scoped>

</style>
