<template>
  <ac-base-notification :notification="notification" :asset-link="productLink">
    <span slot="title"><router-link :to="productLink">New Product: {{event.data.product.name}}</router-link></span>
    <span slot="subtitle"><router-link :to="productLink">By {{event.data.product.user.username}} starting at ${{event.data.product.price}}</router-link></span>
  </ac-base-notification>
</template>

<script>
  import AcBaseNotification from './ac-base-notification'
  import Notifiction from '../../mixins/notification'
  export default {
    name: 'ac-new-character',
    components: {AcBaseNotification},
    mixins: [Notifiction],
    computed: {
      productLink () {
        if (this.event.data.product) {
          return {
            name: 'Product',
            params: {
              productID: this.event.data.product.id
            }
          }
        }
      }
    }
  }
</script>

<style scoped>

</style>