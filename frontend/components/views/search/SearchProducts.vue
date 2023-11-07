<template>
  <v-container fluid class="pa-0">
    <ac-paginated :list="list" :track-pages="true" :auto-run="false">
      <template v-slot:default>
        <v-col class="pa-1" cols="6" md="4" lg="3" xl="2" v-for="product in list.list" :key="product.x!.id">
          <ac-product-preview :product="product.x" :force-shield="searchForm.fields.shield_only.value"/>
        </v-col>
      </template>
      <template v-slot:empty>
        <v-col class="text-center">
          <v-card>
            <v-card-text>
              We could not find anything which matched your request.
            </v-card-text>
          </v-card>
        </v-col>
      </template>
    </ac-paginated>
  </v-container>
</template>
<script lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'
import {Component, mixins, toNative} from 'vue-facing-decorator'
import SearchList from '@/components/views/search/mixins/SearchList'
import AcProductPreview from '@/components/AcProductPreview.vue'

@Component({
  components: {
    AcProductPreview,
    AcPaginated,
  },
})
class SearchProducts extends mixins(SearchList) {
  public list: ListController<Product> = null as unknown as ListController<Product>

  public created() {
    this.list = this.$getList('searchProducts', {
      endpoint: '/api/sales/search/product/',
      persistent: true,
    })
    this.rawUpdate(this.searchForm.rawData)
  }
}

export default toNative(SearchProducts)
</script>
