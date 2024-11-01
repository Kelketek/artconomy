<template>
  <v-container fluid class="pa-0">
    <ac-paginated :list="list" :track-pages="true" :auto-run="false">
      <template v-slot:default>
        <v-col class="pa-1" cols="6" md="4" lg="3" xl="2" v-for="product in list.list" :key="product.x!.id">
          <ac-product-preview :product="product.x!" :force-shield="searchForm.fields.shield_only.value"/>
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
<script setup lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {useList} from '@/store/lists/hooks.ts'
import {onMounted} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import {useSearchList} from '@/components/views/search/mixins/SearchList.ts'

import type {Product} from '@/types/main'

const searchForm = useForm('search')
const list = useList<Product>('searchProducts', {
  endpoint: '/api/sales/search/product/',
  persistent: true,
})
// We use this debouncedUpdate during testing.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const {rawUpdate} = useSearchList(searchForm, list)
onMounted(() => {
  rawUpdate(searchForm.rawData)
})
</script>
