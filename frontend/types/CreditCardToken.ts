import {PROCESSORS} from '@/types/PROCESSORS'

export interface CreditCardToken {
  id: number,
  last_four: string,
  primary: boolean,
  cvv_verified: boolean,
  type: number,
  processor: PROCESSORS,
}
