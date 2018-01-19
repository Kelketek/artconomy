<template>
  <div>
    <div class="row" v-if="error">
      <div class="col-sm-12 text-center">
        <p>{{error}}</p>
      </div>
    </div>
    <div class="row" v-if="response !== null && nonEmpty">
      <slot name="header"></slot>
      <div class="col-sm-12">
        <b-pagination-nav
            align="center" :use-router="true" :base-url="baseURL" :link-gen="linkGen"
            v-model="currentPage" :per-page="pageSize" :number-of-pages="totalPages"
            v-if="totalPages > 1"
        ></b-pagination-nav>
      </div>
      <div class="col-lg-3 col-md-4 col-sm-6"
           v-for="(asset, key, index) in response.results"
           :key="key" :id="'asset-' + key"
           :asset="asset"
      >
        <ac-gallery-preview :asset="asset" />
      </div>
      <div class="col-sm-12">
        <b-pagination-nav
            align="center" :use-router="true" :base-url="baseURL" :link-gen="linkGen"
            v-model="currentPage" :per-page="pageSize" :number-of-pages="totalPages"
            v-if="totalPages > 1"
        ></b-pagination-nav>
      </div>
    </div>
  </div>
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
    mixins: [Paginated]
  }
</script>

<style scoped>

</style>