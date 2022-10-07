<template>
  <v-container fluid class="pa-0">
    <ac-paginated :list="list" :auto-run="false" :show-pagination="false">
      <template v-slot:default>
        <v-col class="pa-1" cols="6" md="4" lg="3" xl="2" v-for="product in list.list" :key="product.x.id">
          <ac-product-preview :product="product.x" />
        </v-col>
      </template>
      <v-col class="text-center" slot="empty">
        <v-card>
          <v-card-text>
            We could not find anything which matched your request.
          </v-card-text>
        </v-card>
      </v-col>
    </ac-paginated>
  </v-container>
</template>
<script lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'
import Component, {mixins} from 'vue-class-component'
import SearchList from '@/components/views/search/mixins/SearchList'
import AcProductPreview from '@/components/AcProductPreview.vue'
  @Component({
    components: {AcProductPreview, AcPaginated},
  })
export default class SearchProducts extends mixins(SearchList) {
    public list: ListController<Product> = null as unknown as ListController<Product>
    public created() {
      this.list = this.$getList('searchProducts', {
        endpoint: '/api/sales/v1/search/product/',
        persistent: true,
        grow: true,
      })
      this.rawUpdate(this.searchForm.rawData)
    }
}
</script>
