<template>
  <v-row no-gutters>
    <v-col cols="12">
      <ac-product-preview
        :product="product.x!"
        :username="username"
        :linked="false"
        @click.capture.stop.prevent="() => false"
      />
    </v-col>
    <v-col cols="12">
      <v-row>
        <v-col cols="8">
          <ac-patch-field
            :patcher="product.patchers.hidden"
            field-type="v-checkbox"
            label="Hidden"
          />
        </v-col>
        <v-col cols="2">
          <v-btn
            color="green"
            variant="flat"
            class="mt-2"
            :to="{name: 'Product', params: {username, productId: `${product.x!.id}`}}"
          >
            <v-icon :icon="mdiArrowExpand" />
          </v-btn>
        </v-col>
      </v-row>
    </v-col>
    <ac-expanded-property
      v-model="showSettings"
      :large="true"
      :eager="false"
      width="500"
    >
      <template #title>
        <span>Edit Settings</span>
      </template>
      <template #default>
        <v-row>
          <v-col cols="6" />
          <v-col
            cols="6"
            class="text-center"
          >
            <v-btn
              color="green"
              variant="flat"
            >
              View product
            </v-btn>
          </v-col>
          <v-col
            v-if="product.x!.table_product"
            cols="12"
            class="text-center"
          >
            This product is a table product. It is not shown to customers directly.
          </v-col>
        </v-row>
      </template>
    </ac-expanded-property>
  </v-row>
</template>
<script setup lang="ts">
import AcProductPreview from '@/components/AcProductPreview.vue'
import {SingleController} from '@/store/singles/controller.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {ref} from 'vue'
import {mdiArrowExpand} from '@mdi/js'
import type {Product, SubjectiveProps} from '@/types/main'


const props = defineProps<{product: SingleController<Product>} & SubjectiveProps>()
const showSettings = ref(false)
</script>
