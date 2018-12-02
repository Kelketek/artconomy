<template>
  <v-container v-if="response" grid-list-md>
    <slot name="header" v-if="show && header" />
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="error">
        <p>{{error}}</p>
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="show">
        <v-pagination :id="scrollToId" v-model="currentPage" :length="totalPages" :total-visible="10" v-if="totalPages > 1 && !noPagination" />
      </v-flex>
      <ac-product-preview
          v-for="product in growing"
          :key="product.id"
          :product="product"
          :i-frame="iFrame"
          xs12 sm4 lg3
      />
      <v-flex xs12 text-xs-center v-if="show">
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1 && !noPagination" :total-visible="10" @input="performScroll" />
      </v-flex>
      <v-flex v-if="noPagination && to && currentPage !== totalPages" xs12 text-xs-center>
        <v-btn color="primary" :to="to">{{seeMoreText}}</v-btn>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcProductPreview from './ac-product-preview'
  export default {
    props: ['endpoint', 'header', 'noPagination', 'to', 'seeMoreText', 'i-frame'],
    components: {AcProductPreview},
    data () {
      return {
        url: this.endpoint
      }
    },
    created () {
      this.fetchItems()
    },
    watch: {
      rating () {
        this.restart()
      }
    },
    name: 'ac-product-list',
    mixins: [Paginated],
    computed: {
      show () {
        return this.response !== null && this.nonEmpty
      },
      results () {
        if (this.response === null) {
          return []
        } else {
          return this.response.results
        }
      }
    }
  }
</script>

<style scoped>

</style>