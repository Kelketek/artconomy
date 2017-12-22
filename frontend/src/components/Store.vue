<template>
  <div class="storefront container">
    <div class="row">
      <ac-product-preview
        v-for="product in growing"
        :key="product.id"
        v-if="growing !== null && setUp"
        :product="product"
      ></ac-product-preview>
      <div class="col-sm-12" v-if="is_current && !setUp">
        <p>To open a store, you must first set up your
          <router-link :to="{name: 'Settings', params: {tabName: 'payment', 'username': this.viewer.username}}">
            deposit account.
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Paginated from '../mixins/paginated'
  import AcProductPreview from './ac-product-preview'
  import { artCall } from '../lib'

  export default {
    components: {AcProductPreview},
    mixins: [Viewer, Perms, Paginated],
    methods: {
      populateProducts (response) {
        this.response = response
        this.growing = response.results
      }
    },
    computed: {
      setUp () {
        if (!this.is_current) {
          return true
        }
        return this.user.dwolla_configured
      }
    },
    created () {
      artCall(`/api/sales/v1/${this.username}/products/`, 'GET', undefined, this.populateProducts)
    }
  }
</script>
