<template>
  <ac-load-section :controller="productList">
    <v-row v-for="[username, products] of productsByUser" :key="username">
      <v-col cols="12">
        <v-toolbar :dense="true" color="black" :key="`${username}-header`">
          <ac-avatar :username="username" :show-name="false" />
          <v-toolbar-title class="ml-1"><ac-link :to="{name: 'AboutUser', params: {username}}">{{username}}</ac-link></v-toolbar-title>
        </v-toolbar>
      </v-col>
      <v-col cols="12" sm="3" md="4" lg="3" xl="2" v-for="product in products" :key="product.id">
        <div>
          <ac-product-preview :product="product"></ac-product-preview>
        </div>
        <div>
          <v-btn color="green" block :to="{name: 'NewOrder', params: {username, productId: product.id, stepId: 1}}">New Order</v-btn>
        </div>
      </v-col>
    </v-row>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'
import AcProductPreview from '@/components/AcProductPreview.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

@Component({
  components: {AcProductPreview, AcLink, AcAvatar, AcLoadSection},
})
export default class TableProducts extends mixins(Viewer) {
  public productList = null as unknown as ListController<Product>

  public get productsByUser() {
    const result = new Map()
    for (const product of this.productList.list) {
      const username = product.x!.user.username
      if (!result.has(username)) {
        result.set(username, [])
      }
      result.get(username).push(product.x!)
    }
    return result
  }

  public created() {
    this.productList = this.$getList('table_products', {endpoint: '/api/sales/table/products/', paginated: false})
    this.productList.firstRun()
  }
}
</script>
