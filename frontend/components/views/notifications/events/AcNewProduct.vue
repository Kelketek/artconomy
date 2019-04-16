<template>
  <ac-base-notification :notification="notification" :asset-link="productLink">
    <span slot="title"><ac-link :to="productLink">New Product: {{event.data.product.name}}</ac-link></span>
    <span slot="subtitle"><ac-link :to="productLink">By {{event.data.product.user.username}} starting at ${{event.data.product.price}}</ac-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'
import AcLink from '@/components/wrappers/AcLink'

export default {
  name: 'ac-new-character',
  components: {AcLink, AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    productLink() {
      if (this.event.data.product) {
        return {
          name: 'Product',
          params: {
            productID: this.event.data.product.id,
            username: this.event.data.product.user.username,
          },
        }
      }
      return null
    },
  },
}
</script>

<style scoped>

</style>
