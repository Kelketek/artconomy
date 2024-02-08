import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'
import {CreditCardToken} from '@/types/CreditCardToken.ts'
import {AccountType} from '@/types/AccountType.ts'
import {TransactionCategory} from '@/types/TransactionCategory.ts'
import {TransactionStatus} from '@/types/TransactionStatus.ts'

export default interface Transaction {
  id: string,
  source: AccountType,
  destination: AccountType,
  status: TransactionStatus,
  category: TransactionCategory,
  card: CreditCardToken|null,
  payer: RelatedUser|null,
  payee: RelatedUser|null,
  amount: number,
  remote_id: string,
  created_on: string,
  response_message: '',
  finalized_on: string|null,
  targets: any[],
}
