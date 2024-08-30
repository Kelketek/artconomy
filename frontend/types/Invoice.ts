import type {InvoiceStatusValue} from '@/types/InvoiceStatus.ts'
import type {User} from '@/store/profiles/types/User.ts'
import type {InvoiceTypeValue} from '@/types/InvoiceType.ts'

export default interface Invoice {
  id: string,
  created_on: string,
  record_only: boolean,
  bill_to: User,
  issued_by: User,
  targets: any[],
  status: InvoiceStatusValue,
  total: number,
  type: InvoiceTypeValue,
}
