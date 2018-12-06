<template>
  <v-container grid-list-md>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center>
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
      </v-flex>
      <ac-order-preview
          v-for="order in growing"
          :key="order.id"
          v-if="growing !== null"
          :order="order"
          :buyer="buyer"
          :username="username"
      />
      <v-flex xs12 text-xs-center>
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
      </v-flex>
    </v-layout>
  </v-container>
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
    props: {
      buyer: {},
      url: {},
      autoFetch: { default: false }
    },
    data () {
      return {
        baseURL: this.$router.path
      }
    },
    methods: {
      populateOrders (response) {
        this.response = response
        this.growing = response.results
      },
      bootstrap () {
        this.response = null
        this.growing = null
        artCall(this.url, 'GET', undefined, this.populateOrders, this.$error)
      }
    },
    created () {
      this.bootstrap()
    },
    watch: {
      url () {
        this.bootstrap()
      }
    }
  }
</script>

<style scoped>

</style>