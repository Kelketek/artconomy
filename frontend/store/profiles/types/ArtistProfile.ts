import {BankStatus} from '@/store/profiles/types/BankStatus'
import {Ratings} from '@/store/profiles/types/Ratings'

export interface ArtistProfile {
  dwolla_configured: boolean,
  commissions_closed: boolean,
  max_load: number,
  max_rating: Ratings,
  has_products: boolean,
  commission_info: string,
  auto_withdraw: boolean,
  escrow_disabled: boolean,
  bank_account_status: BankStatus,
}
