<template>
  <ac-paginated :list="products" :track-pages="true">
    <v-col cols="12" sm="3" md="4" lg="3" xl="2" v-for="product in products.list" :key="product.x.id" class="pa-1">
      <ac-product-preview :product="product.x"></ac-product-preview>
    </v-col>
  </ac-paginated>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {Prop} from 'vue-property-decorator'
import Viewer from '@/mixins/viewer'
  @Component({
    components: {AcProductPreview, AcPaginated, AcLoadSection},
  })
export default class AcProductList extends mixins(Viewer) {
    @Prop({required: true})
    public products!: ListController<Product>
    public created() {
      this.products.firstRun().catch(this.setError)
    }
}
</script>
