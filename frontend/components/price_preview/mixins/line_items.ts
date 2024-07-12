import {computed} from 'vue'
import LineItem from '@/types/LineItem.ts'
import {ListController} from '@/store/lists/controller.ts'
import {LineTypes} from '@/types/LineTypes.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {getTotals} from '@/lib/lineItemFunctions.ts'

export const useLineItems = (props: {lineItems: ListController<LineItem>}) => {
  const addOnForm = useForm(`${props.lineItems.name.value}_addOn`, {
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
  const extraForm = useForm(`${props.lineItems.name.value}_extra`, {
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
  const rawLineItems = computed(() => props.lineItems.list.map((item) => item.x as LineItem))

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
  const baseItems = computed(() => props.lineItems.list.filter(item => item.x && item.x.type === LineTypes.BASE_PRICE))
  const linesOfType = (type: LineTypes) => props.lineItems.list.filter((item) => item.x!.type === type)
  const addOns = computed(() => linesOfType(LineTypes.ADD_ON))
  const extras = computed(() => linesOfType(LineTypes.EXTRA))
  const taxes = computed(() => linesOfType(LineTypes.TAX))
  const others = computed(() => props.lineItems.list.filter((item) => item.x && [LineTypes.PREMIUM_SUBSCRIPTION, LineTypes.OTHER_FEE, LineTypes.DELIVERABLE_TRACKING].includes(item.x.type)))
  const rawPlusForms = computed(() => {
    return addForms(rawLineItems.value)
  })

  const priceData = computed(() => {
    return getTotals(rawPlusForms.value)
  })

  const rawPrice = computed(() => priceData.value.total)
  return {
    addOnForm,
    extraForm,
    addForms,
    rawLineItems,
    extraFormItem,
    addOnFormItem,
    baseItems,
    addOns,
    extras,
    others,
    taxes,
    priceData,
    rawPrice,
  }
}
