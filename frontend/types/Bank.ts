import {BankAccountType} from '@/types/BankAccountType'

export interface Bank {
  last_four: string,
  type: BankAccountType,
  pending: string,
}
