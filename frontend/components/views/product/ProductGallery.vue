<template>
  <ac-load-section :controller="product">
    <template v-slot:default>
      <v-container>
        <v-btn color="primary" :to="{name: 'Product', params: {username, productId}}"><v-icon>arrow_back</v-icon>Back to {{product.x.name}}</v-btn>
        <ac-paginated :list="gallery" :track-pages="true">
          <template v-slot:default>
            <v-row class="py-3">
              <v-col cols="4" sm="3" lg="2" v-for="linkedSubmission in gallery.list" :key="linkedSubmission.x.submission.id">
                <ac-gallery-preview class="pa-1"
                                    :submission="linkedSubmission.x.submission"
                                    :show-footer="false"
                >
                </ac-gallery-preview>
              </v-col>
            </v-row>
          </template>
        </ac-paginated>
        <v-btn color="primary" :to="{name: 'Product', params: {username, productId}}"><v-icon>arrow_back</v-icon>Back to {{product.x.name}}</v-btn>
      </v-container>
    </template>
  </ac-load-section>
</template>

<style scoped>

</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import ProductCentric from '@/components/views/product/mixins/ProductCentric'
import {ListController} from '@/store/lists/controller'
import LinkedSubmission from '@/types/LinkedSubmission'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

@Component({
  components: {
    AcLoadSection,
    AcGalleryPreview,
    AcPaginated,
  },
})
export default class ProductGallery extends mixins(ProductCentric) {
  public gallery!: ListController<LinkedSubmission>
  public created() {
    this.gallery = this.$getList(`product__${this.productId}__gallery`, {endpoint: `${this.url}samples/`})
    this.gallery.firstRun()
  }
}
</script>
