import {RelatedUser} from '@/store/profiles/types/RelatedUser'
import {CreditCardToken} from '@/types/CreditCardToken'
import {AccountType} from '@/types/AccountType'
import {TransactionCategory} from '@/types/TransactionCategory'
import {TransactionStatus} from '@/types/TransactionStatus'

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
