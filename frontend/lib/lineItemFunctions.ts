// The functions in this file are meant to mirror the functions in backend/apps/sales/utils. There's not a good way
// to ensure that they're both updated at the same time, but they should, hopefully, be easy enough to keep in sync.
// If enough code has to be repeated between the two bases it may be worth looking into a transpiler.
import {LineType} from '@/types/enums/LineType.ts'
import {js_get_totals, js_reckon_lines} from '@/lib/lines'
import type {LineAccumulator, LineItem, LineMoneyMap, LineTypeValue, Pricing, Product} from '@/types/main'

declare type RustedAccumulator = Omit<LineAccumulator, 'subtotals'> & {subtotals: Map<number, string>}

export const getTotals = (lines: LineItem[]): LineAccumulator => {
  let result: RustedAccumulator
  let subtotals: LineMoneyMap
  try {
    result = js_get_totals(lines, 2)
    subtotals = new Map() as LineMoneyMap
    lines.map((line) => subtotals.set(line, result.subtotals.get(line.id)!))
  } catch (err) {
    console.log('GET TOTALS FAILED!')
    console.log(JSON.stringify(lines, null, 2))
    throw err
  }
  return {...result, subtotals}
}

export const reckonLines = (lines: LineItem[]) => {
  try {
    return js_reckon_lines(lines, 2)
  } catch (err) {
    console.log("RECKON_LINES FAILED!")
    console.log(JSON.stringify(lines, null, 2))
    throw err
  }
};

export function totalForTypes(accumulator: LineAccumulator, types: LineTypeValue[]) {
  const relevant = [...accumulator.subtotals.keys()].filter((line: LineItem) => types.includes(line.type))
  const totals = relevant.map((line: LineItem) => parseFloat(accumulator.subtotals.get(line) as string))
  return sum(totals)
}

function sum(list: number[]): string {
  return list.reduce((a: number, b: number) => (a + b), 0).toFixed(2)
}

export function invoiceLines(
  options: {
    planName: string|null|undefined,
    pricing: Pricing|null,
    value: string,
    international: boolean,
    escrowEnabled: boolean,
    product: Product|null,
    cascade: boolean,
  },
) {
  const {planName, pricing, value, international, escrowEnabled, product, cascade} = options
  const extraLines = []
  let addOnPrice = parseFloat(value)
  let basePrice: string
  // eslint-disable-next-line camelcase
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
      amount: addOnPrice.toFixed(2),
      frozen_value: null,
      percentage: '0',
      description: '',
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
  basePrice, tableProduct, cascade, international, pricing, planName, escrowEnabled, extraLines,
}: {
  basePrice: string,
  escrowEnabled: boolean,
  tableProduct: boolean,
  international: boolean,
  cascade: boolean,
  planName: string|null|undefined,
  pricing: Pricing|null,
  extraLines: LineItem[],
}) => {
  if (!planName || !pricing) {
    return []
  }
  if (isNaN(parseFloat(basePrice))) {
    return []
  }
  const plan = pricing?.plans.filter((x) => x.name === planName)[0]
  if (!plan) {
    return []
  }
  const lines: LineItem[] = []
  lines.push({
    id: -1,
    priority: 0,
    type: LineType.BASE_PRICE,
    amount: basePrice,
    frozen_value: null,
    percentage: '0',
    description: '',
    cascade_amount: false,
    cascade_percentage: false,
    back_into_percentage: false,
  })
  if (tableProduct) {
    lines.push({
      id: -3,
      priority: 400,
      type: LineType.TABLE_SERVICE,
      cascade_percentage: cascade,
      // We don't cascade this flat amount for table products. Might revisit this later.
      cascade_amount: false,
      amount: pricing.table_static,
      frozen_value: null,
      percentage: pricing.table_percentage,
      back_into_percentage: !cascade,
      description: '',
    }, {
      id: -4,
      priority: 700,
      type: LineType.TAX,
      cascade_percentage: cascade,
      cascade_amount: cascade,
      percentage: pricing.table_tax,
      back_into_percentage: true,
      description: '',
      amount: '0',
      frozen_value: null,
    })
  } else if (escrowEnabled) {
    let percentagePrice = plan.shield_percentage_price
    if (international) {
      percentagePrice = (parseFloat(percentagePrice) + parseFloat(pricing.international_conversion_percentage)) + ''
    }
    lines.push({
      id: -5,
      priority: 300,
      type: LineType.SHIELD,
      cascade_percentage: cascade,
      cascade_amount: cascade,
      amount: plan.shield_static_price,
      frozen_value: null,
      percentage: percentagePrice,
      back_into_percentage: !cascade,
      description: '',
    })
  } else if (parseFloat(plan.per_deliverable_price) !== 0) {
    lines.push({
      id: -6,
      priority: 300,
      type: LineType.DELIVERABLE_TRACKING,
      cascade_percentage: cascade,
      cascade_amount: cascade,
      amount: plan.per_deliverable_price,
      frozen_value: null,
      percentage: '0',
      back_into_percentage: !cascade,
      description: '',
    })
  }
  lines.push(...extraLines)
  return lines
}
