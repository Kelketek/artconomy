<template>
  <ac-load-section :controller="product">
    <template #default>
      <v-container v-if="product.x">
        <v-btn
          color="primary"
          :to="{ name: 'Product', params: { username, productId } }"
          variant="flat"
        >
          <v-icon :icon="mdiArrowLeftBold" />
          Back to {{ product.x.name }}
        </v-btn>
        <ac-paginated :list="gallery" :track-pages="true">
          <template #default>
            <v-row class="py-3">
              <v-col
                v-for="linkedSubmission in gallery.list"
                :key="linkedSubmission.x!.submission.id"
                cols="4"
                sm="3"
                lg="2"
              >
                <ac-gallery-preview
                  class="pa-1"
                  :submission="linkedSubmission.x!.submission"
                  :show-footer="false"
                />
              </v-col>
            </v-row>
          </template>
        </ac-paginated>
        <v-btn
          color="primary"
          :to="{ name: 'Product', params: { username, productId } }"
          variant="flat"
        >
          <v-icon :icon="mdiArrowLeftBold" />
          Back to {{ product.x.name }}
        </v-btn>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import { useProduct } from "@/components/views/product/mixins/ProductCentric.ts"

import AcPaginated from "@/components/wrappers/AcPaginated.vue"
import AcGalleryPreview from "@/components/AcGalleryPreview.vue"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import { mdiArrowLeftBold } from "@mdi/js"
import { useList } from "@/store/lists/hooks.ts"

import type {
  LinkedSubmission,
  ProductProps,
  SubjectiveProps,
} from "@/types/main"

const props = defineProps<SubjectiveProps & ProductProps>()
const { product, url } = useProduct(props)
const gallery = useList<LinkedSubmission>(
  `product__${props.productId}__gallery`,
  { endpoint: `${url.value}samples/` },
)
gallery.firstRun()
</script>

<style scoped></style>
