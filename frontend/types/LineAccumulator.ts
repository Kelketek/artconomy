import {LineMoneyMap} from '@/types/LineMoneyMap'
import Big from 'big.js'

export default interface LineAccumulator {
  total: Big,
  subtotals: LineMoneyMap,
  discount: Big,
}
