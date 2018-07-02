<template>
  <ac-base-notification :notification="notification" :asset-link="paymentLink">
    <span slot="title"><router-link :to="paymentLink">There was an issue renewing your subscription.</router-link></span>
    <span slot="subtitle"><router-link :to="paymentLink">The error we got was: {{event.data.error}}</router-link></span>
  </ac-base-notification>
</template>

<script>
  import AcBaseNotification from './ac-base-notification'
  import Notifiction from '../../mixins/notification'
  export default {
    name: 'ac-renewal-failure',
    components: {AcBaseNotification},
    mixins: [Notifiction],
    computed: {
      paymentLink () {
        return {
          name: 'Settings',
          params: {
            username: this.event.target.username,
            tabName: 'payment'
          }
        }
      }
    }
  }
</script>

<style scoped>

</style>