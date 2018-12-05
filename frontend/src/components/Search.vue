<template>
  <v-container>
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
      <v-tab href="#tab-profiles" key="profiles">
        <v-icon>account_circle</v-icon>&nbsp;Profiles <strong>{{tabCounter('profileCount')}}</strong>
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-products">
        <v-layout row justify-center>
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
        <div v-if="query.q.length === 0" class="text-xs-center pt-2">
          <p>Enter tags to search for, such as 'inks', 'color', 'shaded', 'digital', 'fullbody', or 'refsheet'.</p>
        </div>
        <v-expansion-panel v-model="showAdvanced">
          <v-expansion-panel-content>
            <div slot="header">Advanced Search Options</div>
            <v-card>
              <v-card-text>
                <ac-form-container :schema="productSchema" :model="productModel"></ac-form-container>
              </v-card-text>
            </v-card>
          </v-expansion-panel-content>
        </v-expansion-panel>
        <ac-product-list ref="productSearch" class="pt-2" counter-name="productCount" endpoint="/api/sales/v1/search/product/" :query-data="query" />
      </v-tab-item>
      <v-tab-item id="tab-assets">
        <v-layout justify-center>
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
        <div v-if="query.q.length === 0" class="text-xs-center pt-2">
          <p>Enter tags to search for, like 'fox', 'pony', 'chibi', or 'refsheet'.</p>
        </div>
        <ac-asset-gallery ref="assetSearch" counter-name="assetCount" class="pt-2" endpoint="/api/profiles/v1/search/asset/" :query-data="query" />
      </v-tab-item>
      <v-tab-item id="tab-characters">
        <v-layout row justify-center>
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
        <div v-if="query.q.length === 0" class="text-xs-center pt-2">
          <p>Enter tags to search for, like 'fox', 'wolf', 'human', 'male' or 'female'.</p>
        </div>
        <characters ref="characterSearch" counter-name="characterCount" class="pt-2" endpoint="/api/profiles/v1/search/character/" :query-data="query" />
      </v-tab-item>
      <v-tab-item id="tab-profiles">
        <v-layout row justify-center>
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
        <div v-if="query.q.length === 0" class="text-xs-center pt-2">
          <p>Enter a name to search for.</p>
        </div>
        <ac-user-gallery ref="profileSearch" counter-name="profileCount" class="pt-2" endpoint="/api/profiles/v1/search/user/" :query-data="query" />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
  import AcAssetGallery from './ac-asset-gallery'
  import {paramHandleMap, EventBus, querySyncer, queryVal, setMetaContent} from '../lib'
  import Characters from './Characters'
  import AcUserGallery from './ac-user-gallery'
  import AcFormContainer from './ac-form-container'
  import debounce from 'lodash.debounce'
  import AcProductList from './ac-product-list'

  export default {
    components: {
      AcProductList,
      AcFormContainer,
      AcUserGallery,
      Characters,
      AcAssetGallery},
    name: 'search',
    props: ['tabName'],
    data () {
      return {
        characterCount: 0,
        assetCount: 0,
        productCount: 0,
        profileCount: 0,
        showAdvanced: null,
        productModel: {
          shield_only: false,
          by_rating: false,
          featured: false,
          min_price: null,
          max_price: null,
          watchlist_only: false
        },
        query: {
          q: this.$route.query['q'] || [],
          max_price: [],
          min_price: [],
          shield_only: [],
          by_rating: [],
          watchlist_only: []
        },
        productSchema: {
          fields: [
            {
              type: 'v-text',
              inputType: 'number',
              label: 'Max Price (USD)',
              model: 'max_price',
              step: '.01',
              featured: true,
              required: false
            }, {
              type: 'v-text',
              inputType: 'number',
              label: 'Min Price (USD)',
              model: 'min_price',
              step: '.01',
              featured: true,
              required: false
            }, {
              type: 'v-checkbox',
              styleClasses: ['vue-checkbox'],
              label: 'Sort by Rating',
              model: 'by_rating',
              required: false,
              hint: "If checked, sorts products by the artist's rating."
            }, {
              type: 'v-checkbox',
              styleClasses: ['vue-checkbox'],
              label: 'Only Featured Products',
              model: 'featured',
              required: false,
              hint: "If checked, only shows featured products."
            }, {
              type: 'v-checkbox',
              styleClasses: ['vue-checkbox'],
              label: 'Shield only',
              model: 'shield_only',
              required: false,
              hint: 'If checked, only shows products protected by the Artconomy Shield escrow service.'
            }
          ]
        }
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
      },
      queryUpdate: debounce(function () {
        this.query = {
          q: this.$route.query['q'] || '',
          max_price: this.productModel.max_price || [],
          min_price: this.productModel.min_price || [],
          featured: this.productModel.featured || [],
          shield_only: this.productModel.shield_only || [],
          by_rating: this.productModel.by_rating || [],
          watchlist_only: this.productModel.watchlist_only || []
        }
      }, 500)
    },
    watch: {
      'productModel.shield_only': querySyncer('shield_only'),
      'productModel.by_rating': querySyncer('by_rating'),
      'productModel.featured': querySyncer('featured'),
      'productModel.max_price': querySyncer('max_price'),
      'productModel.min_price': querySyncer('min_price'),
      'productModel.watchlist_only': querySyncer('watchlist_only'),
      productModel: {
        deep: true,
        immediate: true,
        handler () {
          this.queryUpdate()
        }
      },
      queryField () {
        this.queryUpdate()
      }
    },
    computed: {
      queryField: {
        get () {
          let base = this.$route.query['q'] || []
          for (let val of base) {
            val = val.replace(/[\W_]+/g, '')
          }
          return base.join(' ')
        },
        set (value) {
          let queryData = value.split(' ')
          let query = []
          for (let val of queryData) {
            if (val !== '') {
              query.push(val)
            }
          }
          let newQuery = {...this.$route.query}
          newQuery.q = query
          this.$router.history.replace({name: 'Search', query: newQuery, params: this.$route.params})
        }
      },
      tab: paramHandleMap('tabName')
    },
    created () {
      this.productModel.shield_only = queryVal(this, 'shield_only', false)
      this.productModel.featured = queryVal(this, 'featured', false)
      this.productModel.by_rating = queryVal(this, 'by_rating', false)
      this.productModel.min_price = queryVal(this, 'min_price', null)
      this.productModel.max_price = queryVal(this, 'max_price', null)
      this.productModel.watchlist_only = queryVal(this, 'watchlist_only', false)
      if (this.tab === 'tab-undefined') {
        this.tab = 'tab-products'
      }
      if (this.isLoggedIn) {
        this.productSchema.fields.push({
          type: 'v-checkbox',
          styleClasses: ['vue-checkbox'],
          label: 'On my Watchlist',
          model: 'watchlist_only',
          required: false,
          hint: 'If checked, only returns results from your watchlist.'
        })
      }
      if (Object.values(this.productModel).some((x) => { return x })) {
        this.showAdvanced = 0
      }
      EventBus.$on('result-count', this.setCounter)
      document.title = `Search - Artconomy`
      setMetaContent('description', 'Search for artists, art, and products.')
    }
  }
</script>

<style scoped>

</style>