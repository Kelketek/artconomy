<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <span slot="title"><router-link
      :to="assetLink">Your waitlist has been updated. You now have {{event.data.count}} orders on your waitlist.</router-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notification from '../mixins/notification'

export default {
  name: 'ac-waitlist-updated',
  mixins: [Notification],
  components: {AcBaseNotification},
  data() {
    return {}
  },
  computed: {
    assetLink() {
      return {
        name: 'WaitingSales',
        params: {
          username: this.event.target.username,
        },
      }
    },
  },
}
</script>
