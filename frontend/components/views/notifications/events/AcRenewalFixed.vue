<template>
  <ac-base-notification :notification="notification" :asset-link="transactionLink">
    <span slot="title"><router-link
        :to="transactionLink">Your subscription has renewed successfully!</router-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'

export default {
  name: 'ac-renewal-fixed',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    transactionLink() {
      return {
        name: 'Settings',
        params: {
          username: this.event.target.username,
          tabName: 'payment',
          subTabName: 'transactions',
          tertiaryTabName: 'purchases',
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
