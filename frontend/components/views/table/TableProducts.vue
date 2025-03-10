<template>
  <ac-load-section :controller="productList">
    <v-row
      v-for="[username, products] of productsByUser"
      :key="username"
    >
      <v-col cols="12">
        <v-toolbar
          :key="`${username}-header`"
          :dense="true"
          color="black"
        >
          <ac-avatar
            :username="username"
            :show-name="false"
            class="ml-3"
          />
          <v-toolbar-title class="ml-1">
            <ac-link :to="{name: 'AboutUser', params: {username}}">
              {{ username }}
            </ac-link>
          </v-toolbar-title>
        </v-toolbar>
      </v-col>
      <v-col
        v-for="product in products"
        :key="product.id"
        cols="12"
        sm="3"
        md="4"
        lg="3"
        xl="2"
      >
        <div>
          <ac-product-preview :product="product" />
        </div>
        <div>
          <v-btn
            color="green"
            block
            :to="{name: 'NewOrder', params: {username, productId: product.id, stepId: 1}}"
            variant="flat"
          >
            New
            Order
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcProductPreview from '@/components/AcProductPreview.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {computed} from 'vue'
import {useList} from '@/store/lists/hooks.ts'
import type {Product} from '@/types/main'

const productsByUser = computed(() => {
  const result = new Map()
  for (const product of productList.list) {
    const username = product.x!.user.username
    if (!result.has(username)) {
      result.set(username, [])
    }
    result.get(username).push(product.x!)
  }
  return result
})

const productList = useList<Product>('table_products', {
  endpoint: '/api/sales/table/products/',
  paginated: false,
})
productList.firstRun()
</script>
