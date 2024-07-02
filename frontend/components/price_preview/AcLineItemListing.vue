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
      <v-col class="text-left pl-1" cols="6">${{rawPrice.toFixed(2)}}</v-col>
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
import {getTotals, totalForTypes} from '@/lib/lineItemFunctions.ts'
import {LineTypes} from '@/types/LineTypes.ts'
import {ListController} from '@/store/lists/controller.ts'
import {computed} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'

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

const addOnForm = useForm(`${props.lineItems.name}_addOn`, {
  endpoint: props.lineItems.endpoint,
  fields: {
    amount: {
      value: 0,
      validators: [{name: 'numeric'}],
    },
    description: {value: ''},
    type: {value: LineTypes.ADD_ON},
    percentage: {value: 0},
  },
})
const extraForm = useForm(`${props.lineItems.name}_extra`, {
  endpoint: props.lineItems.endpoint,
  fields: {
    amount: {
      value: 0,
      validators: [{name: 'numeric'}],
    },
    description: {value: ''},
    type: {value: LineTypes.EXTRA},
    percentage: {value: 0},
  },
})

const rawLineItems = computed(() => props.lineItems.list.map((item) => item.x as LineItem))
const baseItems = computed(() => props.lineItems.list.filter(item => item.x && item.x.type === LineTypes.BASE_PRICE))

const modifiers = computed(() => rawLineItems.value.filter(
      // We include tips here since we will handle that with a different interface.
      (line: LineItem) => [
        LineTypes.TIP, LineTypes.SHIELD, LineTypes.BONUS, LineTypes.TABLE_SERVICE,
      ].includes(line.type)))

const addOns = computed(() => props.lineItems.list.filter((item) => item.x && item.x.type === LineTypes.ADD_ON))
const exras = computed(() => props.lineItems.list.filter((item) => item.x && item.x.type === LineTypes.EXTRA))
const others = computed(() => props.lineItems.list.filter((item) => item.x && [LineTypes.PREMIUM_SUBSCRIPTION, LineTypes.OTHER_FEE, LineTypes.DELIVERABLE_TRACKING].includes(item.x.type)))

const addOnFormItem = computed((): LineItem => {
  return {
    id: -105,
    amount: parseFloat(addOnForm.fields.amount.value),
    frozen_value: null,
    cascade_amount: false,
    cascade_percentage: false,
    back_into_percentage: false,
    percentage: parseFloat(addOnForm.fields.percentage.value),
    type: addOnForm.fields.type.value,
    priority: 100,
    description: addOnForm.fields.description.value,
  }
})

const extraFormItem = computed((): LineItem => {
  return {
    id: -106,
    amount: parseFloat(extraForm.fields.amount.value),
    frozen_value: null,
    cascade_amount: false,
    cascade_percentage: false,
    back_into_percentage: false,
    percentage: parseFloat(extraForm.fields.percentage.value),
    type: extraForm.fields.type.value,
    priority: 400,
    description: extraForm.fields.description.value,
  }
})

const addForms = (startingItems: LineItem[]) => {
  const allItems = [...startingItems]
  const addOnValue = parseFloat(addOnForm.fields.amount.value)
  if (addOnValue && !isNaN(addOnValue)) {
    allItems.push(addOnFormItem.value)
  }
  const extraValue = parseFloat(extraForm.fields.amount.value)
  if (extraValue && !isNaN(extraValue)) {
    allItems.push(extraFormItem.value)
  }
  return allItems
}

const rawPlusForms = computed(() => {
  return addForms(rawLineItems.value)
})

const priceData = computed(() => {
  return getTotals(rawPlusForms.value)
})

const rawPrice = computed(() => priceData.value.total)

const linesOfType = (type: LineTypes) => props.lineItems.list.filter((item) => item.x!.type === type)

const extras = computed(() => linesOfType(LineTypes.EXTRA))

const taxes = computed(() => linesOfType(LineTypes.TAX))

</script>
