// The functions in this file are meant to mirror the functions in backend/apps/sales/utils. There's not a good way
// to ensure that they're both updated at the same time, but they should, hopefully, be easy enough to keep in sync.
// If enough code has to be repeated between the two bases it may be worth looking into a transpiler.
import LineItem from '@/types/LineItem'
import {LineMoneyMap} from '@/types/LineMoneyMap'
import LineAccumulator from '@/types/LineAccumulator'
import {LineTypes} from '@/types/LineTypes'
import Big from 'big.js'
import {ListController} from '@/store/lists/controller'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'
import Product from '@/types/Product'
import {ServicePlan} from '@/types/ServicePlan'

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

export function distributeReduction(total: Big, distributedAmount: Big, lineValues: LineMoneyMap): LineMoneyMap {
  const reductions: LineMoneyMap = new Map()
  if (total.eq(Big('0'))) {
    return reductions
  }
  for (const line of lineValues.keys()) {
    const originalValue = lineValues.get(line) as Big
    if (originalValue.lt(Big(0))) {
      continue
    }
    const multiplier = originalValue.div(total)
    reductions.set(line, distributedAmount.times(multiplier))
  }
  return reductions
}

export function priorityTotal(current: LineAccumulator, prioritySet: LineItem[]): LineAccumulator {
  const currentTotal = current.total
  const subtotals = current.subtotals
  let discount = current.discount
  const workingSubtotals: LineMoneyMap = new Map()
  const summableTotals: LineMoneyMap = new Map()
  const reductions: LineMoneyMap[] = []
  for (const line of prioritySet) {
    // Percentages with equal priorities should not stack.
    let cascadedAmount = Big(0)
    let addedAmount = Big(0)
    let workingAmount: Big
    const staticAmount = Big(line.amount)
    if (line.cascade_amount) {
      cascadedAmount = cascadedAmount.plus(staticAmount)
    } else {
      addedAmount = addedAmount.plus(staticAmount)
    }
    const multiplier = Big('0.01').times(Big(line.percentage))
    if (line.back_into_percentage) {
      if (line.cascade_percentage) {
        workingAmount = currentTotal.div(multiplier.plus(Big('1.00'))).times(multiplier)
      } else {
        const factor = Big('1.00').div(Big('1.00').minus(multiplier))
        let additional = Big('0.00')
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
    if (!cascadedAmount.eq(Big(0))) {
      for (const key of subtotals.keys()) {
        /* istanbul ignore else */
        if (key.priority < line.priority) {
          lineValues.set(key, subtotals.get(key) as Big)
        }
      }
      reductions.push(distributeReduction(currentTotal.minus(discount), cascadedAmount, lineValues))
    }
    if (!addedAmount.eq(Big(0))) {
      summableTotals.set(line, addedAmount)
    }
    workingSubtotals.set(line, workingAmount)
    if (workingAmount.lt(Big('0'))) {
      discount = discount.plus(workingAmount)
    }
  }
  const newSubtotals: LineMoneyMap = new Map([...subtotals])
  for (const reductionSet of reductions) {
    for (const line of reductionSet.keys()) {
      const reduction = reductionSet.get(line) as Big
      newSubtotals.set(line, (newSubtotals.get(line) as Big).minus(reduction))
    }
  }
  const addOn = sum([...summableTotals.values()])
  const newTotals = new Map([...newSubtotals, ...workingSubtotals])
  return {total: currentTotal.plus(addOn), subtotals: newTotals, discount}
}

export function toDistribute(total: Big, map: LineMoneyMap): Big {
  const values = [...map.values()]
  const combinedSum = sum(values.map((value: Big) => value.round(2, 0)))
  const difference = total.round(2, 0).minus(combinedSum)
  const upperBound = Big(values.length).times(Big('0.01'))
  /* istanbul ignore if */
  if (difference.gt(upperBound)) {
    throw Error(`Too many fractions! ${difference} > {upperBound}`)
  }
  return difference
}

export function biggestFirst(a: [LineItem, Big], b: [LineItem, Big]): number {
  // Sort function for [LineItem, Big] pairs, used for allocating reduction amounts.
  const aLineItem = a[0]
  const aAmount = a[1]
  const bLineItem = b[0]
  const bAmount = b[1]
  if (aAmount.eq(bAmount)) {
    return bLineItem.id - aLineItem.id
  } else {
    return parseFloat(bAmount.minus(aAmount).toExponential())
  }
}

export function distributeDifference(difference: Big, map: LineMoneyMap): LineMoneyMap {
  // After all amounts are floored, there are likely to be leftover pennies. Distribute
  // them in the most sane way possible.
  const updatedMap = new Map(map)
  const testMap = new Map(map)
  for (const key of testMap.keys()) {
    const amount = testMap.get(key) as Big
    testMap.set(key, amount.minus(amount.round(2, 0)))
  }
  const sortedValues = [...testMap].sort(biggestFirst)
  let remaining = difference
  for (const key of updatedMap.keys()) {
    updatedMap.set(key, updatedMap.get(key)!.round(2, 0))
  }
  while (remaining.gt(Big('0'))) {
    const amount = Big('0.01')
    const key = sortedValues.shift()![0]
    updatedMap.set(key, updatedMap.get(key)!.plus(amount))
    remaining = remaining.minus(amount)
  }
  return updatedMap
}

export function normalizedLines(prioritySets: Array<LineItem[]>) {
  const baseSet = prioritySets.reduce(
    priorityTotal, {total: Big(0), discount: Big(0), subtotals: new Map() as LineMoneyMap} as LineAccumulator)
  baseSet.total = baseSet.total.round(2, 0)
  const difference = toDistribute(baseSet.total, baseSet.subtotals)
  if (difference.gt(Big('0'))) {
    baseSet.subtotals = distributeDifference(difference, baseSet.subtotals)
  }
  return baseSet
}

export function getTotals(lines: LineItem[]): LineAccumulator {
  const prioritySets = linesByPriority(lines)
  return normalizedLines(prioritySets)
}

export function reckonLines(lines: LineItem[]): Big {
  const totals = getTotals(lines)
  return totals.total.round(2, 0)
}

export function quantize(value: Big) {
  return Big(value.toFixed(2))
}

export function totalForTypes(accumulator: LineAccumulator, types: LineTypes[]) {
  const relevant = [...accumulator.subtotals.keys()].filter((line: LineItem) => types.includes(line.type))
  const totals = relevant.map((line: LineItem) => accumulator.subtotals.get(line) as Big)
  return sum(totals).round(2, 0)
}

export function sum(list: Big[]): Big {
  return list.reduce((a: Big, b: Big) => (a.plus(b)), Big(0))
}

export function invoiceLines(
  options: {
    planName: string|null|undefined,
    pricing: Pricing|null,
    value: string,
    escrowDisabled: boolean,
    product: Product|null,
    cascade: boolean,
  },
) {
  const {planName, pricing, value, escrowDisabled, product, cascade} = options
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
    escrowDisabled,
    tableProduct,
    cascade,
    extraLines,
  })
  // const shieldLines: LineItem[] = [
  //   {
  //     id: -5,
  //     priority: 300,
  //     type: LineTypes.SHIELD,
  //     cascade_percentage: true,
  //     cascade_amount: cascade,
  //     back_into_percentage: false,
  //     amount: plan.shield_static_price,
  //     frozen_value: null,
  //     percentage: plan.shield_percentage_price,
  //     description: '',
  //   },
  // ]
  // if (product) {
  //   lines.push({
  //     id: -1,
  //     priority: 0,
  //     type: LineTypes.BASE_PRICE,
  //     amount: product.base_price,
  //     frozen_value: null,
  //     percentage: 0,
  //     description: '',
  //     cascade_amount: false,
  //     cascade_percentage: false,
  //     back_into_percentage: false,
  //   })
  //   addOnPrice = addOnPrice - product.starting_price
  //   if (!isNaN(addOnPrice) && addOnPrice) {
  //     lines.push({
  //       id: -2,
  //       priority: 100,
  //       type: LineTypes.ADD_ON,
  //       amount: addOnPrice,
  //       frozen_value: null,
  //       percentage: 0,
  //       description: '',
  //       cascade_amount: false,
  //       cascade_percentage: false,
  //       back_into_percentage: false,
  //     })
  //   }
  //   if (product.table_product) {
  //     lines.push({
  //       id: -3,
  //       priority: 400,
  //       type: LineTypes.TABLE_SERVICE,
  //       cascade_percentage: cascade,
  //       cascade_amount: false,
  //       back_into_percentage: false,
  //       amount: pricing.table_static,
  //       frozen_value: null,
  //       percentage: pricing.table_percentage,
  //       description: '',
  //     }, {
  //       id: -4,
  //       priority: 700,
  //       type: LineTypes.TAX,
  //       cascade_percentage: cascade,
  //       cascade_amount: cascade,
  //       back_into_percentage: true,
  //       percentage: pricing.table_tax,
  //       description: '',
  //       amount: 0,
  //       frozen_value: null,
  //     })
  //   } else if (!escrowDisabled) {
  //     lines.push(...shieldLines)
  //   }
  // } else if (!isNaN(addOnPrice)) {
  //   lines.push({
  //     id: -1,
  //     priority: 0,
  //     type: LineTypes.BASE_PRICE,
  //     amount: addOnPrice,
  //     frozen_value: null,
  //     percentage: 0,
  //     description: '',
  //     cascade_amount: false,
  //     cascade_percentage: false,
  //     back_into_percentage: false,
  //   })
  //   if (!escrowDisabled) {
  //     lines.push(...shieldLines)
  //   }
  // }
  // if (escrowDisabled && plan.per_deliverable_price && (!(product && product.table_product))) {
  //   lines.push({
  //     id: -6,
  //     priority: 115,
  //     type: LineTypes.DELIVERABLE_TRACKING,
  //     cascade_percentage: true,
  //     cascade_amount: cascade,
  //     back_into_percentage: false,
  //     amount: plan.per_deliverable_price,
  //     frozen_value: null,
  //     percentage: 0,
  //     description: '',
  //   })
  // }
  // return lines
}

export const deliverableLines = ({
  basePrice, tableProduct, cascade, pricing, planName, escrowDisabled, extraLines,
}: {
  basePrice: number,
  escrowDisabled: boolean,
  tableProduct: boolean,
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
      id: -2,
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
      id: -3,
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
  } else if (!escrowDisabled) {
    lines.push({
      id: -4,
      priority: 300,
      type: LineTypes.SHIELD,
      cascade_percentage: cascade,
      cascade_amount: cascade,
      amount: plan.shield_static_price,
      frozen_value: null,
      percentage: plan.shield_percentage_price,
      back_into_percentage: !cascade,
      description: '',
    })
  }
  lines.push(...extraLines)
  console.log(lines)
  return lines
}
