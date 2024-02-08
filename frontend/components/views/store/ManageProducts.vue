<template>
  <v-row no-gutters>
    <v-col cols="12">
      <v-card-text class="text-center">
        Click (or tap) and drag to rearrange your products. Drag onto the 'next' or
        'previous' button to put the submission before or after to shift them into the
        next or previous page. When you are finished, tap the 'finish' button.
      </v-card-text>
    </v-col>
    <v-col cols="12">
      <ac-draggable-list :list="list">
        <template v-slot:default="{element, index}">
          <v-col cols="12" sm="3" md="4" lg="3" xl="2" class="draggable-item">
            <ac-product-manager :product="element" :username="username" :key="index"/>
          </v-col>
        </template>
      </ac-draggable-list>
    </v-col>
  </v-row>
</template>

<style>
.disabled {
  opacity: .5;
}

.page-setter .sortable-ghost {
  display: none;
}

.page-setter .sortable-ghost + .v-card {
  filter: brightness(200%);
}

.page-setter .sortable-ghost + .v-card.disabled {
  filter: brightness(100%);
}

.unavailable {
  opacity: .5;
}
</style>

<script setup lang="ts">
import {flatten} from '@/lib/lib.ts'
import AcDraggableList from '@/components/AcDraggableList.vue'
import Product from '@/types/Product.ts'
import AcProductManager from '@/components/views/store/AcProductManager.vue'
import {computed} from 'vue'
import {useList} from '@/store/lists/hooks.ts'


declare interface ManageProductsArgs {
  username: string,
}

const props = defineProps<ManageProductsArgs>()

const url = computed(() => `/api/sales/account/${props.username}/products/manage/`)

const list = useList<Product>(`${flatten(props.username)}-products-management`, {endpoint: url.value})
list.firstRun()
</script>
