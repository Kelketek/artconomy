<template>
  <div class="wrapper">
    <v-text-field ref="searchField" :label="schema.label" v-model="query" class="form-control" @focus="runQuery" @input="runQuery" @keydown.enter.prevent.native="grabFirst" :placeholder="schema.placeholder" :error-messages="errors" />
    <div class="mb-2 mt-2">
      <div v-if="productIDs.length === 0 && !schema.hint">Click a product to select it, or press enter to add the first one.</div>
      <div v-else-if="schema.hint" v-html="schema.hint"></div>
      <v-chip light close v-for="product in products" :key="product.id" @input="delProduct(product)" >{{product.name}}</v-chip>
    </div>
    <v-layout v-if="response" class="product-search-results" row wrap>
      <v-flex xs12 md4 lg3
           v-for="(product, index) in response.results"
           :product="product"
           :key="product.id"
      >
        <ac-product-preview :product="product"
                            :class="{primary: index === 0}" class="pt-1"
                            @click.native.prevent.capture="addProduct(product)"
        ></ac-product-preview>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
  import { abstractField } from 'vue-form-generator'
  import Viewer from '../../mixins/viewer'
  import { artCall, EventBus } from '../../lib'
  import materialField from './materialField'
  import AcProductPreview from '../ac-product-preview'

  export default {
    components: {
      AcProductPreview

    },
    name: 'fieldProductSearch',
    mixins: [ Viewer, abstractField, materialField ],
    data () {
      let data = {
        query: '',
        response: null
      }
      if (this.schema.multiple) {
        data.products = []
        data.productIDs = this.value
      } else {
        data.products = []
        data.productIDs = this.value ? [this.value] : []
      }
      return data
    },
    watch: {
      value (newVal) {
        if (Array.isArray(newVal) && newVal.length === 0) {
          this.products = []
          this.productIDs = newVal
        }
        EventBus.$emit('products-selected-' + this.schema.model, this.products)
      }
    },
    methods: {
      runQuery () {
        artCall(`/api/sales/v1/search/product/mine/`, 'GET', {
          q: this.query,
          size: 9,
          tagging: this.schema.tagging
        }, this.populateResponse)
      },
      populateResponse (response) {
        this.response = response
      },
      addProduct (product) {
        if (this.productIDs.indexOf(product.id) === -1) {
          if (this.schema.multiple) {
            this.products.push(product)
            this.productIDs.push(product.id)
            this.$emit('input', this.productIDs)
            this.value = this.productIDs
          } else {
            this.products = [product]
            this.productIDs = [product.id]
            this.$emit('input', this.productIDs[0])
            this.value = product.id
          }
          this.query = ''
          this.response = null
        }
      },
      delProduct (product) {
        let index = this.productIDs.indexOf(product.id)
        if (index > -1) {
          this.productIDs.splice(index, 1)
        }
        index = this.products.indexOf(product)
        if (index > -1) {
          this.products.splice(index, 1)
        }
      },
      grabFirst () {
        if (this.query === '') {
          this.$parent.$parent.submit()
        }
        if (this.response && this.response.results.length) {
          this.addProduct(this.response.results[0])
        }
      }
    }
  }
</script>