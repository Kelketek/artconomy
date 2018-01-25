<template>
  <div>
    <div class="container">
      <b-tabs v-model="tab">
        <b-tab :title="faIcon('gift') + 'Products' + tabCounter('productCount')">
          <div v-if="query.q.length === 0" class="text-center pt-2">
            <p>Enter tags to search for in the search bar above</p>
          </div>
          <store ref="productSearch" class="pt-2" counter-name="productCount" endpoint="/api/sales/v1/search/product/" :query-data="query" />
        </b-tab>
        <b-tab :title="faIcon('picture-o') + 'Submissions' + tabCounter('assetCount')">
          <div v-if="query.q.length === 0" class="text-center pt-2">
            <p>Enter tags to search for in the search bar above</p>
          </div>
          <ac-asset-gallery ref="assetSearch" counter-name="assetCount" class="pt-2" endpoint="/api/profiles/v1/search/asset/" :query-data="query" />
        </b-tab>
        <b-tab :title="faIcon('users') + 'Characters' + tabCounter('characterCount')">
          <div v-if="query.q.length === 0" class="text-center pt-2">
            <p>Enter tags to search for in the search bar above</p>
          </div>
          <characters ref="characterSearch" counter-name="characterCount" class="pt-2" endpoint="/api/profiles/v1/search/character/" :query-data="query" />
        </b-tab>
      </b-tabs>
    </div>
  </div>
</template>

<script>
  import AcAssetGallery from './ac-asset-gallery'
  import { paramHandleMap, EventBus } from '../lib'
  import Characters from './Characters'
  import Store from './Store'

  let TabMap = {
    products: 0,
    submissions: 1,
    characters: 2
  }

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
      faIcon (iconName) {
        return `<i class='fa fa-${iconName}'></i> `
      },
      tabCounter (propName) {
        if (this[propName]) {
          return ` <strong>(${this[propName]})</strong>`
        }
        return ''
      }
    },
    computed: {
      query: {
        get () {
          return {q: this.$route.query['q'] || []}
        }
      },
      tab: paramHandleMap('tabName', TabMap, undefined)
    },
    created () {
      EventBus.$on('result-count', this.setCounter)
      console.log(this.tabName)
    }
  }
</script>

<style scoped>

</style>