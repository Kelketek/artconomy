<template>
  <v-row no-gutters>
    <v-col cols="12">
      <v-card-text class="text-center">
        Click (or tap) and drag to rearrange your products. Drag onto the 'next'
        or 'previous' button to put the submission before or after to shift them
        into the next or previous page. When you are finished, tap the 'finish'
        button.
      </v-card-text>
    </v-col>
    <v-col cols="12">
      <ac-draggable-list :list="list">
        <template #default="{ element, index }">
          <v-col :key="index" cols="12" sm="3" md="4" lg="3" xl="2">
            <ac-product-manager
              :key="index"
              :product="element"
              :username="username"
            />
          </v-col>
        </template>
      </ac-draggable-list>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { flatten } from "@/lib/lib.ts"
import AcDraggableList from "@/components/AcDraggableList.vue"
import AcProductManager from "@/components/views/store/AcProductManager.vue"
import { computed } from "vue"
import { useList } from "@/store/lists/hooks.ts"
import type { Product } from "@/types/main"

declare interface ManageProductsArgs {
  username: string
}

const props = defineProps<ManageProductsArgs>()

const url = computed(
  () => `/api/sales/account/${props.username}/products/manage/`,
)

const list = useList<Product>(
  `${flatten(props.username)}-products-management`,
  { endpoint: url.value },
)
list.firstRun()
</script>

<style>
.disabled {
  opacity: 0.5;
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
  opacity: 0.5;
}
</style>
