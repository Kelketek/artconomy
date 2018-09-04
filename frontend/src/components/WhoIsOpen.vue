<template>
  <v-container grid-list-md>
    <v-tabs v-model="tab" fixed-tabs class="mb-2" v-if="isLoggedIn">
      <v-tab href="#tab-watchlist">Watchlist</v-tab>
      <v-tab href="#tab-all">All</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab" v-if="isLoggedIn">
      <v-tab-item id="tab-watchlist">
        <store class="pt-2" endpoint="/api/sales/v1/who-is-open/" counter-name="watchlist-open" :show-error="true" empty-error="No one on your watchlist is currently open." />
      </v-tab-item>
      <v-tab-item id="tab-all">
        <store class="pt-2" endpoint="/api/sales/v1/new-products/" :show-error="true" empty-error="There are no products currently open." />
      </v-tab-item>
    </v-tabs-items>
    <store class="pt-2" endpoint="/api/sales/v1/new-products/" :show-error="true" empty-error="There are no products currently open." v-else />
  </v-container>
</template>

<script>
  import Store from './Store'
  import Paginated from '../mixins/paginated'
  import Perms from '../mixins/permissions'
  import Viewer from '../mixins/viewer'
  import {paramHandleMap, EventBus} from '../lib'

  export default {
    name: 'WhoIsOpen',
    components: {Store},
    mixins: [Paginated, Perms, Viewer],
    methods: {
      resultCheck (data) {
        if (data.name === 'watchlist-open') {
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

<style scoped>

</style>