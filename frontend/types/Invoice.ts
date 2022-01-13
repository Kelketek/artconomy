import {TerseUser} from '@/store/profiles/types/TerseUser'
import {InvoiceStatus} from '@/types/InvoiceStatus'

export default interface Invoice {
  id: string,
  created_on: string,
  bill_to: TerseUser,
  status: InvoiceStatus,
}
