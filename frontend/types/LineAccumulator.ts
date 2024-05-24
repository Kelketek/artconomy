import {LineMoneyMap} from '@/types/LineMoneyMap.ts'

export default interface LineAccumulator {
  total: string,
  subtotals: LineMoneyMap,
  discount: string,
}
