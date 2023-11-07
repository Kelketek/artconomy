<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      <router-link :to="assetLink">{{event.data.token.product.user.username}} has issued you an order token for
        {{event.data.token.product.name}}
      </router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">Click here to use it!</router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'

export default {
  name: 'ac-order-token-issued',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      return {
        name: 'Product',
        params: {
          username: this.event.data.token.product.user.username,
          productID: this.event.data.token.product.id,
        },
        query: {
          order_token: this.event.data.token.activation_code,
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
