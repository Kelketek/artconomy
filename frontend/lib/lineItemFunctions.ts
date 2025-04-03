// The functions in this file are meant to mirror the functions in backend/apps/sales/utils. There's not a good way
// to ensure that they're both updated at the same time, but they should, hopefully, be easy enough to keep in sync.
// If enough code has to be repeated between the two bases it may be worth looking into a transpiler.
import { LineType } from "@/types/enums/LineType.ts"
import {
  js_get_totals,
  js_reckon_lines,
  js_deliverable_lines,
} from "@/lib/lines"
import type {
  LineAccumulator,
  LineItem,
  LineMoneyMap,
  LineTypeValue,
  Pricing,
  Product,
} from "@/types/main"
import { LineCategory } from "@/types/enums/LineCategory.ts"

declare type RustedAccumulator = Omit<LineAccumulator, "subtotals"> & {
  subtotals: Map<number, string>
}

export const getTotals = (lines: LineItem[]): LineAccumulator => {
  let result: RustedAccumulator
  let subtotals: LineMoneyMap
  try {
    result = js_get_totals(lines, 2)
    subtotals = new Map() as LineMoneyMap
    lines.map((line) => subtotals.set(line, result.subtotals.get(line.id)!))
  } catch (err) {
    console.log("GET TOTALS FAILED!")
    console.log(JSON.stringify(lines, null, 2))
    throw err
  }
  return { ...result, subtotals }
}

export const reckonLines = (lines: LineItem[]) => {
  try {
    return js_reckon_lines(lines, 2)
  } catch (err) {
    console.log("RECKON_LINES FAILED!")
    console.log(JSON.stringify(lines, null, 2))
    throw err
  }
}

export function totalForTypes(
  accumulator: LineAccumulator,
  types: LineTypeValue[],
) {
  const relevant = [...accumulator.subtotals.keys()].filter((line: LineItem) =>
    types.includes(line.type),
  )
  const totals = relevant.map((line: LineItem) =>
    parseFloat(accumulator.subtotals.get(line) as string),
  )
  return sum(totals)
}

function sum(list: number[]): string {
  return list.reduce((a: number, b: number) => a + b, 0).toFixed(2)
}

export function invoiceLines(options: {
  planName: string | null | undefined
  pricing: Pricing | null
  value: string
  international: boolean
  escrowEnabled: boolean
  product: Product | null
  cascade: boolean
}) {
  const {
    planName,
    pricing,
    value,
    international,
    escrowEnabled,
    product,
    cascade,
  } = options
  const extraLines = []
  let addOnPrice = parseFloat(value)
  let basePrice: string

  const tableProduct = !!product?.table_product
  if (product) {
    addOnPrice = addOnPrice - parseFloat(product.starting_price)
    basePrice = product.base_price
  } else {
    basePrice = addOnPrice.toFixed(2)
    addOnPrice = 0
  }
  if (!isNaN(addOnPrice) && addOnPrice) {
    extraLines.push({
      id: -2,
      priority: 100,
      type: LineType.ADD_ON,
      category: LineCategory.ESCROW_HOLD,
      amount: addOnPrice.toFixed(2),
      frozen_value: null,
      percentage: "0",
      description: "",
      cascade_amount: false,
      cascade_percentage: false,
      back_into_percentage: false,
    })
  }
  return deliverableLines({
    basePrice,
    planName,
    pricing,
    international,
    escrowEnabled,
    tableProduct,
    cascade,
    extraLines,
  })
}

export const deliverableLines = ({
  basePrice,
  tableProduct,
  cascade,
  escrowEnabled,
  international,
  extraLines,
  planName,
  pricing,
}: {
  basePrice: string
  tableProduct: boolean
  cascade: boolean
  escrowEnabled: boolean
  international: boolean
  extraLines: LineItem[]
  planName: string | null | undefined
  pricing: Pricing | null
}) => {
  if (!planName) {
    return []
  }
  if (isNaN(parseFloat(basePrice))) {
    return []
  }
  if (!pricing) {
    return []
  }
  const plan = pricing.plans.filter((plan) => plan.name === planName)[0]
  if (!plan) {
    return []
  }
  try {
    return js_deliverable_lines({
      base_price: basePrice,
      table_product: tableProduct,
      cascade,
      escrow_enabled: escrowEnabled,
      international: international,
      extra_lines: extraLines,
      plan_name: planName,
      pricing,
    }).Ok
  } catch (err) {
    console.log("DELIVERABLE LINES FAILED!!")
    throw err
  }
}
