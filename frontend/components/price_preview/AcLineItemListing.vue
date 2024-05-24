<template>
  <v-container fluid class="pa-0">
    <template v-if="editable && editBase">
      <ac-line-item-editor :line="line" v-for="line in baseItems" :key="line.x!.id" :price-data="priceData"
                           :editing="editable"/>
    </template>
    <template v-else>
      <ac-line-item-preview :line="line.x!" v-for="line in baseItems" :key="line.x!.id" :price-data="priceData"
                            :editing="editable"/>
    </template>
    <template v-if="editable && editBase">
      <ac-line-item-editor :line="line" v-for="line in addOns" :key="line.x!.id" :price-data="priceData"
                           :editing="editable"/>
      <ac-form-container v-bind="addOnForm.bind">
        <ac-form @submit.prevent="addOnForm.submitThen(lineItems.uniquePush)">
          <ac-new-line-item :form="addOnForm"/>
        </ac-form>
      </ac-form-container>
    </template>
    <template v-else>
      <ac-line-item-preview :line="line.x!" v-for="line in addOns" :key="line.x!.id" :price-data="priceData"/>
    </template>
    <ac-line-item-preview :line="line" v-for="line in modifiers" :key="line.id" :price-data="priceData"
                          :editing="editable"/>
    <template v-if="editable && editExtras">
      <ac-line-item-editor :line="line" v-for="line in extras" :key="line.x!.id" :price-data="priceData"
                           :editing="editable"/>
      <ac-form-container v-bind="extraForm.bind">
        <ac-form @submit.prevent="extraForm.submitThen(lineItems.uniquePush)">
          <ac-new-line-item :form="extraForm"/>
        </ac-form>
      </ac-form-container>
    </template>
    <template v-else>
      <ac-line-item-preview :line="line.x!" v-for="line in extras" :key="line.x!.id" :price-data="priceData"/>
    </template>
    <ac-line-item-preview :line="line.x!" v-for="line in others" :key="line.x!.id" :price-data="priceData"/>
    <ac-line-item-preview :line="line.x!" v-for="line in taxes" :key="line.x!.id" :price-data="priceData"/>
    <v-row no-gutters>
      <v-col class="text-right pr-1" cols="6"><strong>Total Price:</strong></v-col>
      <v-col class="text-left pl-1" cols="6">${{rawPrice}}</v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import AcLineItemEditor from '@/components/price_preview/AcLineItemEditor.vue'
import AcNewLineItem from '@/components/price_preview/AcNewLineItem.vue'
import AcLineItemPreview from '@/components/price_preview/AcLineItemPreview.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import LineItem from '@/types/LineItem.ts'
import {LineTypes} from '@/types/LineTypes.ts'
import {ListController} from '@/store/lists/controller.ts'
import {computed} from 'vue'
import {useLineItems} from '@/components/price_preview/mixins/line_items.ts'

const props = withDefaults(defineProps<{
  lineItems: ListController<LineItem>,
  editBase?: boolean,
  editExtras?: boolean,
  editable?: boolean
}>(), {
  editBase: false,
  editExtras: false,
  editable: false,
})

const modifiers = computed(() => rawLineItems.value.filter(
      // We include tips here since we will handle that with a different interface.
      (line: LineItem) => [
        LineTypes.TIP, LineTypes.SHIELD, LineTypes.BONUS, LineTypes.TABLE_SERVICE,
      ].includes(line.type)))


const {
  addOnForm,
  extraForm,
  rawLineItems,
  baseItems,
  addOns,
  extras,
  others,
  taxes,
  priceData,
  rawPrice,
} = useLineItems(props)


</script>
