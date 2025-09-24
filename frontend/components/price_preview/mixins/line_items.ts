import { computed } from "vue"
import { ListController } from "@/store/lists/controller.ts"
import { LineType } from "@/types/enums/LineType.ts"
import { useForm } from "@/store/forms/hooks.ts"
import { getTotals } from "@/lib/lineItemFunctions.ts"
import type { LineItem, LineTypeValue } from "@/types/main"
import { LineCategory } from "@/types/enums/LineCategory.ts"
import { AccountType } from "@/types/enums/AccountType.ts"

export const useLineItems = (props: {
  lineItems: ListController<LineItem>
}) => {
  const addOnForm = useForm(`${props.lineItems.name.value}_addOn`, {
    endpoint: props.lineItems.endpoint,
    fields: {
      amount: {
        value: "0.00",
        validators: [{ name: "numeric" }],
      },
      description: { value: "" },
      type: { value: LineType.ADD_ON },
      category: { value: LineCategory.ESCROW_HOLD },
      percentage: { value: "0" },
    },
  })
  const extraForm = useForm(`${props.lineItems.name.value}_extra`, {
    endpoint: props.lineItems.endpoint,
    fields: {
      amount: {
        value: "0.00",
        validators: [{ name: "numeric" }],
      },
      description: { value: "" },
      type: { value: LineType.EXTRA },
      category: { value: LineCategory.EXTRA_ITEM },
      percentage: { value: "0" },
    },
  })
  const addOnFormItem = computed((): LineItem => {
    return {
      id: -105,
      amount: addOnForm.fields.amount.value,
      frozen_value: null,
      back_into_percentage: false,
      percentage: addOnForm.fields.percentage.value,
      type: addOnForm.fields.type.value,
      category: addOnForm.fields.category.value,
      priority: 100,
      description: addOnForm.fields.description.value,
      destination_account: AccountType.ESCROW,
      destination_user_id: -1,
    }
  })

  const extraFormItem = computed((): LineItem => {
    return {
      id: -106,
      amount: extraForm.fields.amount.value,
      frozen_value: null,
      back_into_percentage: false,
      percentage: extraForm.fields.percentage.value,
      type: extraForm.fields.type.value,
      category: extraForm.fields.category.value,
      priority: 400,
      description: extraForm.fields.description.value,
      destination_account: AccountType.FUND,
      destination_user_id: null,
    }
  })
  const rawLineItems = computed(() =>
    props.lineItems.list.map((item) => item.x as LineItem),
  )

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
  const baseItems = computed(() =>
    props.lineItems.list.filter(
      (item) => item.x && item.x.type === LineType.BASE_PRICE,
    ),
  )
  const linesOfType = (type: LineTypeValue) =>
    props.lineItems.list.filter((item) => item.x!.type === type)
  const addOns = computed(() => linesOfType(LineType.ADD_ON))
  const extras = computed(() => linesOfType(LineType.EXTRA))
  const taxes = computed(() => linesOfType(LineType.TAX))
  const others = computed(() =>
    props.lineItems.list.filter(
      (item) =>
        item.x &&
        (
          [
            LineType.PREMIUM_SUBSCRIPTION,
            LineType.OTHER_FEE,
            LineType.DELIVERABLE_TRACKING,
          ] as LineTypeValue[]
        ).includes(item.x.type),
    ),
  )
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
