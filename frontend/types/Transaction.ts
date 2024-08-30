import type {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'
import type {CreditCardToken} from '@/types/CreditCardToken.ts'
import type {AccountTypeValue} from '@/types/AccountType.ts'
import type {TransactionCategoryValue} from '@/types/TransactionCategory.ts'
import type {TransactionStatusValue} from '@/types/TransactionStatus.ts'

export default interface Transaction {
  id: string,
  source: AccountTypeValue,
  destination: AccountTypeValue,
  status: TransactionStatusValue,
  category: TransactionCategoryValue,
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
