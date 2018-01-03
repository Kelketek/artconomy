<template>
  <div class="row order-list mt-3 mb-3" v-if="response">
    <b-pagination-nav
        align="center" :use-router="true" :base-url="baseURL" :link-gen="linkGen"
        v-model="currentPage" :per-page="pageSize" :number-of-pages="totalPages"
        v-if="totalPages > 1"
    ></b-pagination-nav>
    <ac-order-preview
        v-for="order in growing"
        :key="order.id"
        v-if="growing !== null"
        :order="order"
        :buyer="buyer"
        :username="username"
    />
    <div class="col-sm-12">
      <b-pagination-nav
          align="center" :use-router="true" :base-url="baseURL" :link-gen="linkGen"
          v-model="currentPage" :per-page="pageSize" :number-of-pages="totalPages"
          v-if="totalPages > 1"
      ></b-pagination-nav>
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
    name: 'ac-order-list',
    mixins: [Viewer, Perms, Paginated],
    components: {AcOrderPreview},
    props: ['url', 'buyer'],
    data: {
      baseUrl: this.url,
    },
    methods: {
      populateOrders (response) {
        this.response = response
        this.growing = response.results
      }
    },
    created () {
      artCall(this.url, 'GET', undefined, this.populateOrders, this.$error)
    }
  }
</script>

<style scoped>

</style>