import {RelatedUser} from '@/store/profiles/types/RelatedUser'
import {CreditCardToken} from '@/types/CreditCardToken'

export default interface Transaction {
  id: string,
  source: number,
  destination: number,
  status: number,
  category: number,
  card: CreditCardToken|null,
  payer: RelatedUser|null,
  payee: RelatedUser|null,
  amount: number,
  remote_id: string,
  created_on: string,
  response_message: '',
  finalized_on: string|null,
  target: any,
}
