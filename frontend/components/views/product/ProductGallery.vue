<template>
  <ac-load-section :controller="product">
    <template v-slot:default>
      <v-container v-if="product.x">
        <v-btn color="primary" :to="{name: 'Product', params: {username, productId}}" variant="flat">
          <v-icon :icon="mdiArrowLeftBold"/>
          Back to {{product.x.name}}
        </v-btn>
        <ac-paginated :list="gallery" :track-pages="true">
          <template v-slot:default>
            <v-row class="py-3">
              <v-col cols="4" sm="3" lg="2" v-for="linkedSubmission in gallery.list"
                     :key="linkedSubmission.x!.submission.id">
                <ac-gallery-preview class="pa-1"
                                    :submission="linkedSubmission.x!.submission"
                                    :show-footer="false"
                >
                </ac-gallery-preview>
              </v-col>
            </v-row>
          </template>
        </ac-paginated>
        <v-btn color="primary" :to="{name: 'Product', params: {username, productId}}" variant="flat">
          <v-icon :icon="mdiArrowLeftBold"/>
          Back to {{product.x.name}}
        </v-btn>
      </v-container>
    </template>
  </ac-load-section>
</template>

<style scoped>

</style>

<script setup lang="ts">
import {useProduct} from '@/components/views/product/mixins/ProductCentric.ts'

import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {mdiArrowLeftBold} from '@mdi/js'
import {useList} from '@/store/lists/hooks.ts'
import ProductProps from '@/types/ProductProps.ts'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import LinkedSubmission from '@/types/LinkedSubmission.ts'

const props = defineProps<SubjectiveProps & ProductProps>()
const {product, url} = useProduct(props)
const gallery = useList<LinkedSubmission>(`product__${props.productId}__gallery`, {endpoint: `${url.value}samples/`})
gallery.firstRun()
</script>
