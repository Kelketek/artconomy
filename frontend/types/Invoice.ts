import {InvoiceStatus} from '@/types/InvoiceStatus'
import {User} from '@/store/profiles/types/User'
import {InvoiceType} from '@/types/InvoiceType'

export default interface Invoice {
  id: string,
  created_on: string,
  bill_to: User,
  issued_by: User,
  targets: any[],
  status: InvoiceStatus,
  total: number,
  type: InvoiceType,
}
