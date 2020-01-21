// The functions in this file are meant to mirror the functions in backend/apps/sales/utils. There's not a good way
// to ensure that they're both updated at the same time, but they should, hopefully, be easy enough to keep in sync.
// If enough code has to be repeated between the two bases it may be worth looking into a transpiler.
import LineItem from '@/types/LineItem'
import {LineMoneyMap} from '@/types/LineMoneyMap'
import LineAccumulator from '@/types/LineAccumulator'
import {LineTypes} from '@/types/LineTypes'
import Big from 'big.js'

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
    const multiplier = originalValue.div(total)
    reductions.set(line, distributedAmount.times(multiplier))
  }
  return reductions
}

export function priorityTotal(current: LineAccumulator, prioritySet: LineItem[]): LineAccumulator {
  const currentTotal = current['total']
  const subtotals = current['map']
  const workingSubtotals: LineMoneyMap = new Map()
  const summableTotals: LineMoneyMap = new Map()
  const reductions: LineMoneyMap[] = []
  for (const line of prioritySet) {
    // Percentages with equal priorities should not stack.
    let cascadedAmount = Big(0)
    let addedAmount = Big(0)
    let workingAmount = currentTotal.times(Big('0.01')).times(quantize(Big(line.percentage)))
    const lineValues: LineMoneyMap = new Map()
    if (line.cascade_percentage) {
      cascadedAmount = cascadedAmount.plus(workingAmount)
    } else {
      addedAmount = addedAmount.plus(workingAmount)
    }
    const staticAmount = quantize(Big(line.amount))
    if (line.cascade_amount) {
      cascadedAmount = cascadedAmount.plus(staticAmount)
    } else {
      addedAmount = addedAmount.plus(staticAmount)
    }
    workingAmount = workingAmount.plus(staticAmount)
    if (!cascadedAmount.eq(Big(0))) {
      for (const key of subtotals.keys()) {
        /* istanbul ignore else */
        if (key.priority < line.priority) {
          lineValues.set(key, subtotals.get(key) as Big)
        }
      }
      reductions.push(distributeReduction(currentTotal, cascadedAmount, lineValues))
    }
    if (!addedAmount.eq(Big(0))) {
      summableTotals.set(line, addedAmount)
    }
    workingSubtotals.set(line, workingAmount)
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
  return {total: currentTotal.plus(addOn), map: newTotals}
}

export function getTotals(lines: LineItem[]): LineAccumulator {
  const prioritySets = linesByPriority(lines)
  const baseSet = prioritySets.reduce(priorityTotal, {total: Big(0), map: new Map() as LineMoneyMap} as LineAccumulator)
  for (const key of baseSet.map.keys()) {
    baseSet.map.set(key, quantize(baseSet.map.get(key) as Big))
  }
  return baseSet
}

export function reckonLines(lines: LineItem[]): Big {
  const totals = getTotals(lines)
  return quantize(totals['total'])
}

export function quantize(value: Big) {
  return Big(value.toFixed(2))
}

export function totalForTypes(accumulator: LineAccumulator, types: LineTypes[]) {
  let relevant = [...accumulator.map.keys()].filter((line: LineItem) => types.includes(line.type))
  const totals = relevant.map((line: LineItem) => accumulator.map.get(line) as Big)
  return quantize(sum(totals))
}

export function sum(list: Big[]): Big {
  return list.reduce((a: Big, b: Big) => (a.plus(b)), Big(0))
}
