<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      <router-link :to="assetLink">We had an issue sending money to your bank.</router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">Click here to change your bank settings.</router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification.vue'
import Notification from '../mixins/notification.ts'

export default {
  name: 'ac-withdraw-failed',
  components: {AcBaseNotification},
  mixins: [Notification],
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
