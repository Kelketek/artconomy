<template>
  <v-card v-if="results.length">
    <v-container>
      <v-layout row wrap>
        <v-layout xs12 text-xs-center v-if="error">
          <p>{{error}}</p>
        </v-layout>
        <slot name="header" v-if="show" />
        <v-flex xs12 v-if="show">
          <b-pagination-nav
              align="center" :use-router="true" :base-url="baseURL" :link-gen="linkGen"
              v-model="currentPage" :per-page="pageSize" :number-of-pages="totalPages"
              v-if="totalPages > 1"
          ></b-pagination-nav>
        </v-flex>
        <v-flex xs6 md6 lg3
             v-for="(asset, key, index) in results"
             :key="key" :id="'asset-' + key"
             :asset="asset"
        >
            <ac-gallery-preview :asset="asset" />
        </v-flex>
        <v-flex xs12 v-if="show">
          <b-pagination-nav
              align="center" :use-router="true" :base-url="baseURL" :link-gen="linkGen"
              v-model="currentPage" :per-page="pageSize" :number-of-pages="totalPages"
              v-if="totalPages > 1"
          ></b-pagination-nav>
        </v-flex>
      </v-layout>
    </v-container>
  </v-card>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcGalleryPreview from './ac-gallery-preview'
  export default {
    props: ['endpoint'],
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