<template>
  <v-container>
    <v-layout hidden-md-and-up row justify-center>
      <v-text-field
          placeholder="Search..."
          single-line
          v-model="queryField"
          append-icon="search"
          @click:append="() => {}"
          color="white"
          hide-details
      />
    </v-layout>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-products" key="product">
        <v-icon>shopping_basket</v-icon>&nbsp;Products <strong>{{tabCounter('productCount')}}</strong>
      </v-tab>
      <v-tab href="#tab-assets" key="submissions">
        <v-icon>image</v-icon>&nbsp;Submissions <strong>{{tabCounter('assetCount')}}</strong>
      </v-tab>
      <v-tab href="#tab-characters" key="characters">
        <v-icon>people</v-icon>&nbsp;Characters <strong>{{tabCounter('characterCount')}}</strong>
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-products">
        <div v-if="query.q.length === 0" class="text-xs-center pt-2">
          <p>Enter tags to search for in the search bar above</p>
        </div>
        <store ref="productSearch" class="pt-2" counter-name="productCount" endpoint="/api/sales/v1/search/product/" :query-data="query" />
      </v-tab-item>
      <v-tab-item id="tab-assets">
        <div v-if="query.q.length === 0" class="text-xs-center pt-2">
          <p>Enter tags to search for in the search bar above</p>
        </div>
        <ac-asset-gallery ref="assetSearch" counter-name="assetCount" class="pt-2" endpoint="/api/profiles/v1/search/asset/" :query-data="query" />
      </v-tab-item>
      <v-tab-item id="tab-characters">
        <div v-if="query.q.length === 0" class="text-xs-center pt-2">
          <p>Enter tags to search for in the search bar above</p>
        </div>
        <characters ref="characterSearch" counter-name="characterCount" class="pt-2" endpoint="/api/profiles/v1/search/character/" :query-data="query" />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
  import AcAssetGallery from './ac-asset-gallery'
  import { paramHandleMap, EventBus } from '../lib'
  import Characters from './Characters'
  import Store from './Store'

  export default {
    components: {
      Store,
      Characters,
      AcAssetGallery},
    name: 'search',
    props: ['tabName'],
    data () {
      return {
        characterCount: 0,
        assetCount: 0,
        productCount: 0
      }
    },
    methods: {
      emptyResult (ref) {
        return ref && (ref.growing !== null) && (ref.growing.length === 0)
      },
      setCounter (counterData) {
        this[counterData.name] = counterData.count
      },
      tabCounter (propName) {
        if (this[propName]) {
          return `(${this[propName]})`
        }
        return ''
      }
    },
    computed: {
      queryField: {
        get () {
          return this.$route.query['q'] || ''
        },
        set (value) {
          let queryData = value.split(' ')
          let query = []
          for (let val of queryData) {
            if (val !== '') {
              query.push(val)
            }
          }
          this.$router.history.replace({name: 'Search', query: {q: query}, params: this.$route.params})
        }
      },
      query: {
        get () {
          return {q: this.$route.query['q'] || []}
        }
      },
      tab: paramHandleMap('tabName')
    },
    created () {
      if (this.tab === 'tab-undefined') {
        this.tab = 'tab-products'
      }
      EventBus.$on('result-count', this.setCounter)
    }
  }
</script>

<style scoped>

</style>