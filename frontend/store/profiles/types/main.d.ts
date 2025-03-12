import { BankStatus } from "@/store/profiles/types/enums.ts"
import { SingleState } from "@/store/singles/types"
import { RatingsValue } from "@/types/main"

export interface AnonUser {
  rating: RatingsValue
  blacklist: string[]
  nsfw_blacklist: string[]
  sfw_mode: boolean
  username: "_"
  birthday: null | string
  artist_mode?: undefined
  avatar_url?: undefined
  is_staff?: undefined
  is_superuser?: undefined
  verified_adult: boolean
}

export type BankStatusValue = (typeof BankStatus)[keyof typeof BankStatus]

export interface ArtistProfile {
  dwolla_configured: boolean
  commissions_closed: boolean
  max_load: number
  public_queue: boolean
  has_products: boolean
  commission_info: string
  auto_withdraw: boolean
  escrow_enabled: boolean
  lgbt: boolean
  artist_of_color: boolean
  bank_account_status: BankStatusValue
}

export interface ProfileModuleOpts {
  persistent?: boolean
  viewer?: boolean
}

export interface User {
  landscape_paid_through: string | null
  telegram_link: string
  watching: boolean
  blocking: boolean
  rating: RatingsValue
  sfw_mode: boolean
  username: string
  id: number
  guest: boolean
  is_staff: boolean
  is_superuser: boolean
  avatar_url: string
  email: string
  guest_email: string
  favorites_hidden: boolean
  blacklist: string[]
  nsfw_blacklist: string[]
  biography: string
  taggable: boolean
  stars: number | null
  rating_count: number
  landscape: boolean
  international: boolean
  landscape_enabled: boolean
  artist_mode: boolean
  hits: number
  watches: number
  birthday: string | null
  service_plan: string
  next_service_plan: string
  verified_email: boolean
  paypal_configured: boolean
  verified_adult: boolean
}

export interface ProfileState {
  user?: SingleState<User>
  artistProfile?: SingleState<ArtistProfile>
  persistent: boolean
  viewer: boolean
}

export interface RelatedUser {
  id: number
  username: string
  avatar_url: string
  stars: number | null
  rating_count: number
  is_staff: boolean
  is_superuser: boolean
  artist_mode: boolean | null
  guest: boolean
  taggable: boolean
  verified_email: boolean
}

export type StaffPower =
  | "handle_disputes"
  | "view_social_data"
  | "view_financials"
  | "moderate_content"
  | "moderate_discussion"
  | "table_seller"
  | "view_as"
  | "administrate_users"

export interface StaffPowers extends Record<StaffPower, boolean> {
  id: number
}

export interface TerseUser {
  id: number
  username: string
  avatar_url: string
  biography: string
  has_products: boolean
  favorites_hidden: boolean
  watching: boolean
  blocking: boolean
  stars: number | null
  is_staff: boolean
  is_superuser: boolean
  artist_mode: boolean | null
  taggable: boolean
  hits: number
  watches: number
  guest: boolean
  // Not actually here, but avoids issues with compatibility elsewhere.
  sfw_mode: boolean
  verified_email: boolean
  service_plan: string
  landscape: boolean
  international: boolean
}

export interface UserStoreState {
  // Username we are acting as
  viewerRawUsername: null | string
  userModules: { [key: string]: ProfileState }
}
