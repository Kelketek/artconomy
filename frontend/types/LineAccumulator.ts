import {LineMoneyMap} from '@/types/LineMoneyMap.ts'
import {Decimal} from 'decimal.js'

export default interface LineAccumulator {
  total: Decimal,
  subtotals: LineMoneyMap,
  discount: Decimal,
}
