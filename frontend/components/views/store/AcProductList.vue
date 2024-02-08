<template>
  <ac-paginated :list="products" :track-pages="true">
    <v-col cols="12" sm="3" md="4" lg="3" xl="2" v-for="product in products.list" :key="product.x!.id" class="pa-1">
      <ac-product-preview :product="product.x" :show-username="false" :mini="mini"/>
    </v-col>
    <template v-slot:empty>
    </template>
  </ac-paginated>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import {ListController} from '@/store/lists/controller.ts'
import Product from '@/types/Product.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import Viewer from '@/mixins/viewer.ts'

@Component({
  components: {
    AcProductPreview,
    AcPaginated,
    AcLoadSection,
  },
  mixins: [Viewer],
})
class AcProductList extends mixins(Viewer) {
  @Prop({required: true})
  public products!: ListController<Product>

  @Prop({default: false})
  public mini!: boolean

  public created() {
    this.products.firstRun().catch(this.setError)
  }
}

export default toNative(AcProductList)
</script>
