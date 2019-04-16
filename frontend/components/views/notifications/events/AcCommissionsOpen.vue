<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <span slot="title"><router-link :to="assetLink">{{event.target.username}} is open!</router-link></span>
    <span slot="subtitle"><router-link :to="assetLink">Click here to commission them.</router-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'

export default {
  name: 'ac-commissions-open',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      return {
        name: 'Profile',
        params: {
          username: this.event.target.username,
          tabName: 'products',
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
