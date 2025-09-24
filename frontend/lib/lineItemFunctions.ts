// The functions in this file are meant to mirror the functions in backend/apps/sales/utils. There's not a good way
// to ensure that they're both updated at the same time, but they should, hopefully, be easy enough to keep in sync.
// If enough code has to be repeated between the two bases it may be worth looking into a transpiler.
import {
  js_get_totals,
  js_reckon_lines,
  js_deliverable_lines,
  js_invoice_lines,
  js_sum,
} from "@/lib/lines"
import type {
  LineAccumulator,
  LineItem,
  LineMoneyMap,
  LineTypeValue,
  Pricing,
  Product,
} from "@/types/main"
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
  const totals = relevant.map(
    (line: LineItem) => accumulator.subtotals.get(line) as string,
  )
  return sum(totals)
}

export function invoiceLines(options: {
  planName: string | null
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
  try {
    return js_invoice_lines({
      plan_name: planName,
      pricing,
      value,
      international,
      escrow_enabled: escrowEnabled,
      product,
      cascade,
      user_id: -1,
      allow_soft_failure: true,
      quantization: 2,
    }).Ok
  } catch (err) {
    console.log("INVOICE_LINES FAILED!")
    console.log(JSON.stringify(options, null, 2))
    throw err
  }
}

export const sum = (values: string[]): string => {
  return js_sum(values, 2)
}

export const deliverableLines = ({
  basePrice,
  tableProduct,
  escrowEnabled,
  international,
  extraLines,
  planName,
  pricing,
}: {
  basePrice: string
  tableProduct: boolean
  escrowEnabled: boolean
  international: boolean
  extraLines: LineItem[]
  planName: string | null
  pricing: Pricing | null
}) => {
  return js_deliverable_lines({
    base_price: basePrice,
    table_product: tableProduct,
    escrow_enabled: escrowEnabled,
    international: international,
    extra_lines: extraLines,
    plan_name: planName,
    pricing,
    user_id: -1,
    quantization: 2,
    allow_soft_failure: true,
  }).Ok
}
