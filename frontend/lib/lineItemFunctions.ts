// The functions in this file are meant to mirror the functions in backend/apps/sales/utils. There's not a good way
// to ensure that they're both updated at the same time, but they should, hopefully, be easy enough to keep in sync.
// If enough code has to be repeated between the two bases it may be worth looking into a transpiler.
import LineItem from '@/types/LineItem'
import {LineMoneyMap} from '@/types/LineMoneyMap'
import LineAccumulator from '@/types/LineAccumulator'
import {LineTypes} from '@/types/LineTypes'
import {Decimal} from 'decimal.js'
import Pricing from '@/types/Pricing'
import Product from '@/types/Product'

// Match Python's decimal defaults.
Decimal.set({rounding: Decimal.ROUND_HALF_EVEN})
// Python internally marks its precision as 28, but checking
// the output of both shows that Decimal seems to have an off-by-one
// error here, or else counts differently.
Decimal.set({precision: 28})

type AnyFunction = (...args: any[]) => any

export function decimalContext(policy: Partial<Decimal.Config>) {
  return function halfEvenContext<T extends AnyFunction>(func: T): ((...args: Parameters<T>) => ReturnType<T>) {
    return (...args: Parameters<T>): ReturnType<T> => {
      const oldSettings: Omit<Decimal.Config, 'defaults'> = {
        precision: Decimal.precision,
        rounding: Decimal.rounding,
        toExpNeg: Decimal.toExpNeg,
        toExpPos: Decimal.toExpPos,
        minE: Decimal.minE,
        maxE: Decimal.maxE,
        crypto: Decimal.crypto,
        modulo: Decimal.modulo,
      }
      Decimal.set(policy)
      const result = func(...args)
      Decimal.set(oldSettings)
      return result
    }
  }
}

export const halfEvenContext = decimalContext({rounding: Decimal.ROUND_HALF_EVEN})

export const downContext = decimalContext({rounding: Decimal.ROUND_DOWN})

export function linesByPriority(lines: LineItem[]): Array<LineItem[]> {
  const prioritySets: {[key: number]: LineItem[]} = {}
  for (const line of lines) {
    prioritySets[line.priority] = prioritySets[line.priority] || []
    prioritySets[line.priority].push(line)
  }
  const priorities = Object.keys(prioritySets).map((key: string) => parseInt(key))
  priorities.sort()
  const result = []
  for (const key of priorities) {
    result.push(prioritySets[key])
  }
  return result
}

export function distributeReduction(total: Decimal, distributedAmount: Decimal, lineValues: LineMoneyMap): LineMoneyMap {
  const reductions: LineMoneyMap = new Map()
  const lineCount = new Decimal([...lineValues.keys()].length)
  for (const line of lineValues.keys()) {
    const originalValue = lineValues.get(line) as Decimal
    // Don't apply reductions to discounts, as that would be nonsense.
    if (originalValue.lt(new Decimal(0))) {
      continue
    }
    let multiplier: Decimal
    if (total.eq(new Decimal('0'))) {
      // If our total is zero, our inputs are zero, and we have to apportion evenly, not
      // proportionally.
      multiplier = new Decimal('1.00').div(lineCount)
    } else {
      multiplier = originalValue.div(total)
    }
    reductions.set(line, distributedAmount.times(multiplier))
  }
  return reductions
}

export const priorityTotal = halfEvenContext((current: LineAccumulator, prioritySet: LineItem[]): LineAccumulator => {
  const currentTotal = current.total
  const subtotals = current.subtotals
  let discount = current.discount
  const workingSubtotals: LineMoneyMap = new Map()
  const summableTotals: LineMoneyMap = new Map()
  const reductions: LineMoneyMap[] = []
  for (const line of prioritySet) {
    // Percentages with equal priorities should not stack.
    let cascadedAmount = new Decimal(0)
    let addedAmount = new Decimal(0)
    let workingAmount: Decimal
    const staticAmount = new Decimal(line.amount)
    if (line.cascade_amount) {
      cascadedAmount = cascadedAmount.plus(staticAmount)
    } else {
      addedAmount = addedAmount.plus(staticAmount)
    }
    const multiplier = new Decimal('0.01').times(new Decimal(line.percentage))
    if (line.back_into_percentage) {
      if (line.cascade_percentage) {
        workingAmount = currentTotal.div(multiplier.plus(new Decimal('1.00'))).times(multiplier)
      } else {
        const factor = new Decimal('1.00').div(new Decimal('1.00').minus(multiplier))
        let additional = new Decimal('0.00')
        if (!line.cascade_amount) {
          additional = staticAmount
        }
        const initialAmount = currentTotal.plus(additional)
        workingAmount = initialAmount.times(factor).minus(initialAmount)
      }
    } else {
      workingAmount = currentTotal.times(multiplier)
    }
    const lineValues: LineMoneyMap = new Map()
    if (line.cascade_percentage) {
      cascadedAmount = cascadedAmount.plus(workingAmount)
    } else {
      addedAmount = addedAmount.plus(workingAmount)
    }
    workingAmount = workingAmount.plus(staticAmount)
    if (!cascadedAmount.eq(new Decimal(0))) {
      for (const key of subtotals.keys()) {
        /* istanbul ignore else */
        if (key.priority < line.priority) {
          lineValues.set(key, subtotals.get(key) as Decimal)
        }
      }
      reductions.push(distributeReduction(currentTotal.minus(discount), cascadedAmount, lineValues))
    }
    if (!addedAmount.eq(new Decimal(0))) {
      summableTotals.set(line, addedAmount)
    }
    workingSubtotals.set(line, workingAmount)
    if (workingAmount.lt(new Decimal('0'))) {
      discount = discount.plus(workingAmount)
    }
  }
  const newSubtotals: LineMoneyMap = new Map([...subtotals])
  for (const reductionSet of reductions) {
    for (const line of reductionSet.keys()) {
      const reduction = reductionSet.get(line) as Decimal
      newSubtotals.set(line, (newSubtotals.get(line) as Decimal).minus(reduction))
    }
  }
  const addOn = sum([...summableTotals.values()])
  const newTotals = new Map([...newSubtotals, ...workingSubtotals])
  return {total: currentTotal.plus(addOn), subtotals: newTotals, discount}
})

export const toDistribute = downContext((total: Decimal, map: LineMoneyMap): Decimal => {
  const values = [...map.values()]
  const combinedSum = sum(values.map((value: Decimal) => value.toDP(2)))
  return total.toDP(2).minus(combinedSum)
})

export function redistributionPriority(ascendingPriority: boolean, a: [LineItem, Decimal], b: [LineItem, Decimal]): number {
  // Sort function for [LineItem, Decimal] pairs, used for allocating reduction amounts.
  const aLineItem = a[0]
  const aAmount = a[1]
  const bLineItem = b[0]
  const bAmount = b[1]
  if (!(aLineItem.priority === bLineItem.priority)) {
    if (ascendingPriority) {
      return bLineItem.priority - aLineItem.priority
    }
    return aLineItem.priority - bLineItem.priority
  }
  if (aAmount.eq(bAmount)) {
    return bLineItem.id - aLineItem.id
  } else {
    return parseFloat(bAmount.minus(aAmount).toExponential())
  }
}

export const distributeDifference = downContext((difference: Decimal, map: LineMoneyMap): LineMoneyMap => {
  // After all amounts are floored, there are likely to be leftover pennies. Distribute
  // them in the most sane way possible.
  const updatedMap = new Map(map)
  const testMap = new Map(map)
  for (const key of testMap.keys()) {
    const amount = testMap.get(key) as Decimal
    testMap.set(key, amount.toDP(2))
  }
  const sortFunc = (
    a: [LineItem, Decimal], b: [LineItem, Decimal],
  ) => redistributionPriority(difference.gt(new Decimal('0')), a, b)
  const sortedValues = [...testMap].sort(sortFunc)
  let currentValues = [...sortedValues]
  let remaining = difference
  for (const key of updatedMap.keys()) {
    updatedMap.set(key, updatedMap.get(key)!.toDP(2))
  }
  let delta: Decimal
  if (remaining.gt(new Decimal('0'))) {
    delta = new Decimal('0.01')
  } else {
    delta = new Decimal('-0.01')
  }
  while (!remaining.eq(new Decimal('0'))) {
    if (!currentValues.length) {
      // If we've gone through all the items, start over.
      currentValues = [...sortedValues]
    }
    const key = currentValues.shift()![0]
    updatedMap.set(key, updatedMap.get(key)!.plus(delta))
    remaining = remaining.minus(delta)
  }
  return updatedMap
})

export const normalizedLines = downContext((prioritySets: Array<LineItem[]>) => {
  const baseSet = prioritySets.reduce(
    priorityTotal, {total: new Decimal(0), discount: new Decimal(0), subtotals: new Map() as LineMoneyMap} as LineAccumulator)
  baseSet.total = baseSet.total.toDP(2)
  baseSet.subtotals.forEach((value, key) => {
    baseSet.subtotals.set(key, value.toDP(2))
  })
  const difference = toDistribute(baseSet.total, baseSet.subtotals)
  if (!difference.eq(new Decimal('0'))) {
    baseSet.subtotals = distributeDifference(difference, baseSet.subtotals)
  }
  return baseSet
})

export const getTotals = downContext((lines: LineItem[]): LineAccumulator => {
  const prioritySets = linesByPriority(lines)
  return normalizedLines(prioritySets)
})

export function reckonLines(lines: LineItem[]): Decimal {
  const totals = getTotals(lines)
  return totals.total.toDP(2)
}

export function quantize(value: Decimal) {
  return new Decimal(value.toFixed(2))
}

export function totalForTypes(accumulator: LineAccumulator, types: LineTypes[]) {
  const relevant = [...accumulator.subtotals.keys()].filter((line: LineItem) => types.includes(line.type))
  const totals = relevant.map((line: LineItem) => accumulator.subtotals.get(line) as Decimal)
  return sum(totals).toDP(2)
}

export function sum(list: Decimal[]): Decimal {
  return list.reduce((a: Decimal, b: Decimal) => (a.plus(b)), new Decimal(0))
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
  let basePrice: number
  // eslint-disable-next-line camelcase
  const tableProduct = !!product?.table_product
  if (product) {
    addOnPrice = addOnPrice - product.starting_price
    basePrice = product.base_price
  } else {
    basePrice = addOnPrice
    addOnPrice = 0
  }
  if (!isNaN(addOnPrice) && addOnPrice) {
    extraLines.push({
      id: -2,
      priority: 100,
      type: LineTypes.ADD_ON,
      amount: addOnPrice,
      frozen_value: null,
      percentage: 0,
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
  basePrice: number,
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
  if (isNaN(basePrice)) {
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
    type: LineTypes.BASE_PRICE,
    amount: basePrice,
    frozen_value: null,
    percentage: 0,
    description: '',
    cascade_amount: false,
    cascade_percentage: false,
    back_into_percentage: false,
  })
  if (tableProduct) {
    lines.push({
      id: -3,
      priority: 400,
      type: LineTypes.TABLE_SERVICE,
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
      type: LineTypes.TAX,
      cascade_percentage: cascade,
      cascade_amount: cascade,
      percentage: pricing.table_tax,
      back_into_percentage: true,
      description: '',
      amount: 0,
      frozen_value: null,
    })
  } else if (escrowEnabled) {
    let percentagePrice = plan.shield_percentage_price
    if (international) {
      percentagePrice += pricing.international_conversion_percentage
    }
    lines.push({
      id: -5,
      priority: 300,
      type: LineTypes.SHIELD,
      cascade_percentage: cascade,
      cascade_amount: cascade,
      amount: plan.shield_static_price,
      frozen_value: null,
      percentage: percentagePrice,
      back_into_percentage: !cascade,
      description: '',
    })
  } else if (plan.per_deliverable_price !== 0) {
    lines.push({
      id: -6,
      priority: 300,
      type: LineTypes.DELIVERABLE_TRACKING,
      cascade_percentage: cascade,
      cascade_amount: cascade,
      amount: plan.per_deliverable_price,
      frozen_value: null,
      percentage: 0,
      back_into_percentage: !cascade,
      description: '',
    })
  }
  lines.push(...extraLines)
  return lines
}
