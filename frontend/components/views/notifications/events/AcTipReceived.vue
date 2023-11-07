<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      <router-link :to="assetLink">{{buyerName}} sent you a tip!</router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'
import {deriveDisplayName} from '@/lib/lib'

export default {
  name: 'ac-tip-received',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      return {
        name: 'SaleDeliverableOverview',
        params: {
          orderId: this.event.target.order.id,
          username: this.viewer.username,
          deliverableId: this.event.target.id,
        },
      }
    },
    buyerName() {
      return deriveDisplayName(this.event.target.order.buyer.username)
    },
  },
}
</script>

<style scoped>

</style>
