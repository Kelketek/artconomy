import {BankAccountType} from '@/types/BankAccountType.ts'

export interface Bank {
  last_four: string,
  type: BankAccountType,
  pending: string,
}
