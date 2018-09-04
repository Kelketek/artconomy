<template>
  <v-container grid-list-md>
    <v-tabs v-model="tab" fixed-tabs class="mb-2">
      <v-tab href="#tab-watchlist">Watchlist</v-tab>
      <v-tab href="#tab-all">All</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-watchlist">
        <ac-scrollable-art endpoint="/api/profiles/v1/watch-list-submissions/" counter-name="watchlist-art" />
      </v-tab-item>
      <v-tab-item id="tab-all">
        <ac-scrollable-art endpoint="/api/profiles/v1/recent-art/"/>
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
  import AcGalleryPreview from './ac-gallery-preview'
  import Paginated from '../mixins/paginated'
  import { ObserveVisibility } from 'vue-observe-visibility'
  import {paramHandleMap, EventBus} from '../lib'
  import AcScrollableArt from './ac-scrollable-art'
  export default {
    name: 'RecentArt',
    mixins: [Paginated],
    directives: {
      ObserveVisibility
    },
    components: {AcScrollableArt, AcGalleryPreview},
    data () {
      return {
        url: '/api/profiles/v1/watch-list-submissions/',
        growMode: true
      }
    },
    methods: {
      resultCheck (data) {
        if (data.name === 'watchlist-art') {
          if (data.count === 0) {
            this.tab = 'tab-all'
          }
        }
      }
    },
    computed: {
      tab: paramHandleMap('tabName', [], undefined, 'tab-watchlist')
    },
    created () {
      this.fetchItems()
      EventBus.$on('result-count', this.resultCheck)
    },
    destroyed () {
      EventBus.$off('result-count', this.resultCheck)
    }
  }
</script>