<template>
  <v-container v-if="results.length" grid-list-md>
    <slot name="header" v-if="show && header" />
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="error">
        <p>{{error}}</p>
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="show">
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
      </v-flex>
      <ac-gallery-preview
          :asset="asset"
          v-for="(asset, key, index) in results"
          :key="key" :id="'asset-' + key"
          xs12 sm4 lg3
      />
      <v-flex xs12 text-xs-center v-if="show">
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcGalleryPreview from './ac-gallery-preview'
  export default {
    props: ['endpoint', 'header'],
    components: {AcGalleryPreview},
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
        this.fetchItems()
      }
    },
    name: 'ac-asset-gallery',
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