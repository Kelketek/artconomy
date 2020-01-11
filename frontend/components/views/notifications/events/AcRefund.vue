<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <span slot="title"><router-link :to="assetLink">Sale #{{event.target.id}} was refunded. :(</router-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notification from '../mixins/notification'

export default {
  name: 'ac-refund',
  mixins: [Notification],
  components: {AcBaseNotification},
  data() {
    return {}
  },
  computed: {
    assetLink() {
      return {
        name: 'Sale',
        params: {
          username: this.event.target.seller.username,
          orderId: this.event.target.id,
        },
      }
    },
  },
}
</script>
