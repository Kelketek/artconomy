import {InvoiceStatus} from '@/types/InvoiceStatus'
import {User} from '@/store/profiles/types/User'

export default interface Invoice {
  id: string,
  created_on: string,
  bill_to: User,
  issued_by: User,
  targets: any[],
  status: InvoiceStatus,
}
