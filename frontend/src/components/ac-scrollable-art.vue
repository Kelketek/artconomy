<template>
  <div>
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
        This list is empty, or
        all art is currently above your permitted ratings or on your blacklist.
      </v-flex>
    </v-layout>
    <v-flex xs12 text-xs-center>
      <div v-if="(growing !== null) && furtherPagination" v-observe-visibility="loadMore"></div>
      <div v-if="fetching"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    </v-flex>
  </div>
</template>

<script>
  import AcGalleryPreview from './ac-gallery-preview'
  import Paginated from '../mixins/paginated'
  import { ObserveVisibility } from 'vue-observe-visibility'
  export default {
    name: 'ac-scrollable-art',
    mixins: [Paginated],
    props: ['endpoint'],
    directives: {
      ObserveVisibility
    },
    components: {AcGalleryPreview},
    data () {
      return {
        url: this.endpoint,
        // We're no longer making this autoload on scroll, which means this component is poorly named.
        // growMode: true
      }
    },
    watch: {
      rating () {
        this.restart()
      }
    }
  }
</script>