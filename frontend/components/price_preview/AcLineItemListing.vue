<template>
  <v-container fluid class="pa-0">
    <template v-if="editable && editBase">
      <ac-line-item-editor :line="line" v-for="line in baseItems" :key="line.x.id" :price-data="priceData" :editing="editable" />
    </template>
    <template v-else>
      <ac-line-item-preview :line="line.x" v-for="line in baseItems" :key="line.x.id" :price-data="priceData" :editing="editable" />
    </template>
    <template v-if="editable && editBase">
      <ac-line-item-editor :line="line" v-for="line in addOns" :key="line.x.id" :price-data="priceData" :editing="editable" />
      <ac-form-container v-bind="addOnForm.bind">
        <ac-form @submit.prevent="addOnForm.submitThen(lineItems.push)">
          <ac-new-line-item :form="addOnForm" :price="priceData.map.get(addOnFormItem) || 0" />
        </ac-form>
      </ac-form-container>
    </template>
    <template v-else>
      <ac-line-item-preview :line="line.x" v-for="line in addOns" :key="line.x.id" :price-data="priceData" />
    </template>
    <ac-line-item-preview :line="line" v-for="line in modifiers" :key="line.id" :price-data="priceData" :editing="editable" />
    <template v-if="editable && editExtras">
      <ac-line-item-editor :line="line" v-for="line in extras" :key="line.x.id" :price-data="priceData" :editing="editable" />
      <ac-form-container v-bind="extraForm.bind">
        <ac-form @submit.prevent="extraForm.submitThen(lineItems.push)">
          <ac-new-line-item :form="extraForm" :price="priceData.map.get(extraFormItem) || 0" />
        </ac-form>
      </ac-form-container>
    </template>
    <template v-else>
      <ac-line-item-preview :line="line.x" v-for="line in extras" :key="line.x.id" :price-data="priceData" />
    </template>
    <ac-line-item-preview :line="line.x" v-for="line in others" :key="line.x.id" :price-data="priceData" />
    <ac-line-item-preview :line="line.x" v-for="line in taxes" :key="line.x.id" :price-data="priceData" />
    <v-row no-gutters>
      <v-col class="text-right pr-1" cols="6" ><strong>Total Price:</strong></v-col>
      <v-col class="text-left pl-1" cols="6" >${{rawPrice.toFixed(2)}}</v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcLineItemEditor from '@/components/price_preview/AcLineItemEditor.vue'
import AcNewLineItem from '@/components/price_preview/AcNewLineItem.vue'
import AcLineItemPreview from '@/components/price_preview/AcLineItemPreview.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import LineItem from '@/types/LineItem'
import {getTotals, totalForTypes} from '@/lib/lineItemFunctions'
import {LineTypes} from '@/types/LineTypes'
import LineItemMixin from './mixins/LineItemMixin'

@Component({
  components: {
    AcLineItemEditor,
    AcNewLineItem,
    AcLineItemPreview,
    AcForm,
    AcFormContainer,
  },
})
export default class AcLineItemListing extends mixins(LineItemMixin) {
  public get rawLineItems() {
    return this.lineItems.list.map((item) => item.x as LineItem)
  }

  public get bonus() {
    return totalForTypes(getTotals(this.rawPlusForms), [LineTypes.BONUS])
  }

  public get baseItems() {
    return this.lineItems.list.filter(item => item.x && item.x.type === LineTypes.BASE_PRICE)
  }

  public get modifiers() {
    return this.moddedItems.filter(
      // We include tips here since we will handle that with a different interface.
      (line: LineItem) => [
        LineTypes.TIP, LineTypes.SHIELD, LineTypes.BONUS, LineTypes.TABLE_SERVICE,
      ].includes(line.type))
  }

  public get addOns() {
    return this.lineItems.list.filter((item) => item.x && item.x.type === LineTypes.ADD_ON)
  }

  public get extras() {
    return this.lineItems.list.filter((item) => item.x && item.x.type === LineTypes.EXTRA)
  }

  public get others() {
    return this.lineItems.list.filter((item) => item.x && [LineTypes.PREMIUM_SUBSCRIPTION, LineTypes.OTHER_FEE].includes(item.x.type))
  }
}
</script>
