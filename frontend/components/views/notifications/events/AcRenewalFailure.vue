<template>
  <ac-base-notification :notification="notification" :asset-link="paymentLink">
    <template v-slot:title>
      <router-link
          :to="paymentLink">There was an issue renewing your subscription.
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="paymentLink">The error we got was: {{event.data.error}}</router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'

export default {
  name: 'ac-renewal-failure',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    paymentLink() {
      return {
        name: 'Settings',
        params: {
          username: this.event.target.username,
          tabName: 'payment',
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
