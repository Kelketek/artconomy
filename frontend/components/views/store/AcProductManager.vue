<template>
  <v-row no-gutters>
    <v-col cols="12">
      <ac-product-preview :product="product.x" :username="username" @click.capture.stop.prevent="() => false"
                          :linked="false"/>
    </v-col>
    <v-col cols="12">
      <v-row>
        <v-col cols="8">
          <ac-patch-field :patcher="product.patchers.hidden" field-type="v-checkbox" label="Hidden"/>
        </v-col>
        <v-col cols="2">
          <v-btn color="green" variant="flat" class="mt-2" :to="{name: 'Product', params: {username, productId: `${product.x!.id}`}}">
            <v-icon icon="mdi-open-in_full"/>
          </v-btn>
        </v-col>
      </v-row>
    </v-col>
    <ac-expanded-property v-model="showSettings" :large="true" :eager="false" width="500">
      <template v-slot:title>
        <span>Edit Settings</span>
      </template>
      <template v-slot:default>
        <v-row>
          <v-col cols="6">

          </v-col>
          <v-col cols="6" class="text-center">
            <v-btn color="green" variant="flat">View product</v-btn>
          </v-col>
          <v-col cols="12" v-if="product.x!.table_product" class="text-center">
            This product is a table product. It is not shown to customers directly.
          </v-col>
        </v-row>
      </template>
    </ac-expanded-property>
  </v-row>
</template>
<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import AcProductPreview from '@/components/AcProductPreview.vue'
import Product from '@/types/Product'
import {SingleController} from '@/store/singles/controller'
import Subjective from '@/mixins/subjective'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'

@Component({
  components: {
    AcPatchField,
    AcExpandedProperty,
    AcFormDialog,
    AcProductPreview,
  },
})
class AcProductManager extends mixins(Subjective) {
  @Prop({required: true})
  public product!: SingleController<Product>

  public showSettings = false
}

export default toNative(AcProductManager)
</script>
