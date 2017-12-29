<template>
  <div class="container order-list">
    <div class="row">
      <ac-order-preview
          v-for="order in growing"
          :key="order.id"
          v-if="growing !== null"
          :order="order"
          :buyer="buyer"
          :username="username"
      ></ac-order-preview>
    </div>
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Paginated from '../mixins/paginated'
  import AcOrderPreview from './ac-order-preview'
  import { artCall } from '../lib'

  export default {
    name: 'orders',
    mixins: [Viewer, Perms, Paginated],
    components: {AcOrderPreview},
    props: ['url', 'buyer'],
    methods: {
      populateOrders (response) {
        this.response = response
        this.growing = response.results
      }
    },
    created () {
      artCall(this.url, 'GET', undefined, this.populateOrders)
    }
  }
</script>

<style scoped>

</style>