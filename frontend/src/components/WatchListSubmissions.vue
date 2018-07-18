<template>
  <v-container grid-list-md>
    <v-layout>
      <v-flex text-xs-center>
        <h1>See recent art from your watchlist here!</h1>
      </v-flex>
    </v-layout>
    <v-layout row wrap v-if="growing">
      <ac-gallery-preview
          :asset="asset"
          v-for="(asset, key, index) in growing"
          :key="key" :id="'asset-' + key"
          xs12 sm4 lg3
      />
    </v-layout>
    <v-layout v-if="growing && growing.length === 0">
      <v-flex text-xs-center>
        Your watchlist is empty, the artists you are watching have been tagged in no art, or
        all art is currently above your permitted ratings or on your blacklist.
      </v-flex>
    </v-layout>
    <v-flex xs12 text-xs-center>
      <div v-if="(growing !== null) && furtherPagination" v-observe-visibility="loadMore"></div>
      <div v-if="fetching"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    </v-flex>
  </v-container>
</template>

<script>
  import AcGalleryPreview from './ac-gallery-preview'
  import Paginated from '../mixins/paginated'
  import { ObserveVisibility } from 'vue-observe-visibility'
  export default {
    name: 'WatchListSubmissions',
    mixins: [Paginated],
    directives: {
      ObserveVisibility
    },
    components: {AcGalleryPreview},
    data () {
      return {
        url: '/api/profiles/v1/watch-list-submissions/',
        growMode: true
      }
    },
    created () {
      this.fetchItems()
    }
  }
</script>