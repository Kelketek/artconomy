<template>
  <ac-paginated :list="products" :track-pages="true">
    <v-col cols="12" sm="3" md="4" lg="3" xl="2" v-for="product in products.list" :key="product.x!.id" class="pa-1">
      <ac-product-preview :product="product.x!" :show-username="false" :mini="mini"/>
    </v-col>
    <template v-slot:empty>
    </template>
  </ac-paginated>
</template>

<script setup lang="ts">
import {ListController} from '@/store/lists/controller.ts'
import Product from '@/types/Product.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'

const props = withDefaults(
    defineProps<{products: ListController<Product>, mini?: boolean}>(),
    {mini: false},
)
const {setError} = useErrorHandling()
props.products.firstRun().catch(setError)
</script>
