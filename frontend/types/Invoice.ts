import {InvoiceStatus} from '@/types/InvoiceStatus.ts'
import {User} from '@/store/profiles/types/User.ts'
import {InvoiceType} from '@/types/InvoiceType.ts'

export default interface Invoice {
  id: string,
  created_on: string,
  record_only: boolean,
  bill_to: User,
  issued_by: User,
  targets: any[],
  status: InvoiceStatus,
  total: number,
  type: InvoiceType,
}
