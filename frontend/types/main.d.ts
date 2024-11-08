import type {ListController} from '@/store/lists/controller.ts'
import type {AxiosError} from 'axios'
import type {ArtStore} from '@/store'
import type {SocketManager} from '@/plugins/socket.ts'
import type {SingleController} from '@/store/singles/controller.ts'
import type {SingleRegistry} from '@/store/singles/registry.ts'
import type {ListRegistry} from '@/store/lists/registry.ts'
import type {FormController} from '@/store/forms/form-controller.ts'
import type {FormRegistry} from '@/store/forms/registry.ts'
import type {CharacterController} from '@/store/characters/controller.ts'
import type {CharacterRegistry} from '@/store/characters/registry.ts'
import type {ProfileController} from '@/store/profiles/controller.ts'
import type {ProfileRegistry} from '@/store/profiles/registry.ts'
import type {RegistryRegistry} from '@/store/registry-base.ts'
import type {RouteLocation, RouteLocationNamedRaw, RouteLocationRaw, Router} from 'vue-router'
import type {createApp} from 'vue'
import type {Product} from '@/types/main.d.ts'
import type {SingleModuleOpts} from '@/store/singles/types.d.ts'
import {ProfileModuleOpts, RelatedUser, TerseUser, User} from '@/store/profiles/types/main'
import {AccountType} from '@/types/enums/AccountType.ts'
import {ConnectionStatus} from '@/types/enums/ConnectionStatus.ts'
import {InvoiceType} from '@/types/enums/InvoiceType.ts'
import {LineType} from '@/types/enums/LineType.ts'
import {LogLevels} from '@/types/enums/LogLevels.ts'
import {Ratings} from '@/types/enums/Ratings.ts'
import {TransactionCategory} from '@/types/enums/TransactionCategory.ts'
import {DeliverableStatus} from '@/types/enums/DeliverableStatus.ts'
import {InvoiceStatus} from '@/types/enums/InvoiceStatus.ts'
import {TransactionStatus} from '@/types/enums/TransactionStatus.ts'
import {ViewerType} from '@/types/enums/ViewerType.ts'
import type {ListModuleOpts} from '@/store/lists/types.d.ts'
import {NamelessFormSchema} from '@/store/forms/types/main'
import {Character, CharacterModuleOpts} from '@/store/characters/types/main'

export interface SortableModel {
  display_position: number,
}

export declare interface AcDraggableListProps<T extends SortableModel> {
  trackPages?: boolean,
  okStatuses?: number[],
  failureMessage?: string,
  emptyMessage?: string,
  showPagination?: boolean,
  list: ListController<T>,
}

export declare interface SortableItem<T extends SortableModel> {
  id: T[keyof T],
  controller: SingleController<T>
}

export declare interface AcDraggableNavsProps<T extends SortableModel> {
  sortableList: SortableItem<T>[],
  list: ListController<T>,
}

export interface AcNotification<T, D> {
  event: {
    id: number,
    type: number,
    data: D,
    date: string,
    target: T,
    recalled: boolean,
  },
  read: boolean,
  id: number
}
export type AcServerError = AxiosError<{ detail: any } | Record<string, string[]>>

export type RatingsValue = typeof Ratings[keyof typeof Ratings]

export interface Submission extends Asset {
  id: number,
  title: string,
  caption: string,
  private: boolean,
  created_on: string,
  owner: RelatedUser,
  comment_count: number,
  favorite_count: number,
  rating: RatingsValue,
  tags: string[],
  favorites: boolean,
  subscribed: boolean,
  hits: number,
  display_position: number,
  commission_link: RouteLocationRaw | null,
  comments_disabled: boolean,
  order: { order_id: number, deliverable_id: number } | null,
}

export interface ArtistTag {
  id: number,
  submission: Submission,
  hidden: boolean,
  display_position: number,
  user: RelatedUser,
}

export type ArtVueInterface = ReturnType<typeof createApp> & ArtVueGlobals

export interface ArtVueGlobals {
  _uid: string,
  // Store
  $store: ArtStore,
  // Socket
  $sock: SocketManager,
  // Shortcuts
  $displayImage: (asset: object, thumbName: string) => string,
  // Single module funcs
  $getSingle: (name: string, schema?: SingleModuleOpts<any>, uid?: string) => SingleController<any>,
  $listenForSingle: (name: string, uid?: string) => void,
  $registryForSingle: () => SingleRegistry,
  // List module funcs
  $getList: (name: string, schema?: ListModuleOpts, uid?: string) => ListController<any>,
  $listenForList: (name: string, uid?: string) => void,
  $registryForList: () => ListRegistry,
  // Form module funcs
  $getForm: (name: string, formSchema?: NamelessFormSchema, uid?: string) => FormController,
  $listenForForm: (name: string, uid?: string) => void,
  $registryForForm: () => FormRegistry,
  // Character module funcs
  $getCharacter: (name: string, schema?: CharacterModuleOpts, uid?: string) => CharacterController,
  $listenForCharacter: (name: string, uid?: string) => void,
  $registryForCharacter: () => CharacterRegistry,
  // Profile module funcs
  $getProfile: (name: string, schema?: ProfileModuleOpts, uid?: string) => ProfileController,
  $listenForProfile: (name: string, uid?: string) => void,
  $registryForProfile: () => ProfileRegistry,
  $registries: RegistryRegistry,
  // Vue Router
  $router: Router,
  $route: RouteLocation,
  $nextTick: (callBack?: () => void) => Promise<void>,
  $root: ArtVueInterface,
  $menuTarget: string | false,
  $statusTarget: string | false,
  $snackbarTarget: string | false,
  $modalTarget: string | false,
}

export interface AssetProps {
  compact?: boolean,
  terse?: boolean,
  contain?: boolean,
  popOut?: boolean,
  fallbackImage?: string,
  alt: string,
}

export interface FileSpec {
  [key: string]: string
}

export interface Asset {
  file: FileSpec,
  tags?: string[],
  rating: RatingsValue,
  preview?: FileSpec | null,
}

export interface Attribute {
  id: number,
  key: string,
  value: string,
  sticky: boolean,
}

export interface Balance {
  escrow: string,
  available: string,
  pending: string,
}

export interface SubjectiveProps {
  username: string,
}

export type CharacterProps = SubjectiveProps & { characterName: string }

export interface ClientSecret {
  secret: string,
}

export interface Comment {
  id: number,
  text: string,
  user: TerseUser | null,
  created_on: string,
  edited: boolean,
  edited_on: string,
  deleted: boolean,
  comments: Comment[],
  comment_count: number,
  subscribed: boolean,
  system: boolean,
}

export interface CommissionStats {
  load: number,
  max_load: number,
  delinquent: boolean,
  commissions_closed: boolean,
  commissions_disabled: boolean,
  products_available: number,
  active_orders: number,
  new_orders: number,
  escrow_enabled: boolean,
}

export interface Conversation {
  id: number,
  read: boolean,
  participants: TerseUser[],
  created_on: string,
  last_comment: Comment | null,
}

export interface CreditCardToken {
  id: number,
  last_four: string,
  primary: boolean,
  cvv_verified: boolean,
  type: number,
}

export type DeliverableStatusValue = typeof DeliverableStatus[keyof typeof DeliverableStatus]

export interface Order {
  id: number,
  created_on: string,
  seller: User,
  buyer: User | null,
  customer_email: string,
  customer_display_name: string,
  // This one's read only, available on the preview serializer to help sellers pick out guest users.
  guest_email: string,
  private: boolean,
  hide_details: boolean,
  claim_token: string | null,
  product_name: string,
  display: Asset | null,
  default_path: RouteLocationNamedRaw,
  deliverable_count: number,
  status: DeliverableStatusValue,
  read: boolean,
}

export interface Deliverable {
  id: number,
  name: string,
  created_on: string,
  status: DeliverableStatusValue,
  product: Product | null,
  price: number,
  details: string,
  commission_info: string,
  arbitrator: User | null,
  adjustment: number,
  stream_link: string,
  revisions: number,
  outputs: Submission[],
  subscribed: boolean,
  adjustment_task_weight: number,
  adjustment_expected_turnaround: number,
  adjustment_revisions: number,
  expected_turnaround: number,
  task_weight: number,
  paid_on: null | string,
  trust_finalized: boolean,
  dispute_available_on: null | string,
  auto_finalize_on: null | string,
  started_on: null | string,
  escrow_enabled: boolean,
  revisions_hidden: boolean,
  table_order: boolean,
  international: boolean,
  final_uploaded: boolean,
  rating: RatingsValue,
  display: Asset | null,
  order: Order,
  invoice: string | null,
  tip_invoice: string | null,
  read: boolean,
  cascade_fees: boolean,
  paypal: boolean,
  paypal_token: string,
  notes: string,
}

export interface Inventory {
  count: number,
}

export type InvoiceTypeValue = typeof InvoiceType[keyof typeof InvoiceType]

export type InvoiceStatusValue = typeof InvoiceStatus[keyof typeof InvoiceStatus]

export interface Invoice {
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

export interface Journal {
  id: number,
  subject: string,
  body: string,
  comments_disabled: boolean,
  created_on: string,
  edited_on: string
  edited: boolean,
  subscribed: boolean,
}

export type LineTypeValue = typeof LineType[keyof typeof LineType]

export interface LineItem {
  id: number,
  priority: number,
  amount: string,
  frozen_value: string | null,
  percentage: string,
  cascade_percentage: boolean,
  cascade_amount: boolean,
  back_into_percentage: boolean,
  type: LineTypeValue,
  description: string,
  destination_account?: number | null,
  destination_user?: number | null,
  targets?: Array<{ model: string, id: string | number }>,
}

export type LineMoneyMap = Map<LineItem, string>

export interface LineAccumulator {
  total: string,
  subtotals: LineMoneyMap,
  discount: string,
}

export interface LinkedCharacter {
  id: number,
  character: Character,
  character_id?: number,
}

export interface Reference {
  id: number,
  file: FileSpec,
  owner: string,
  rating: RatingsValue,
  created_on: string,
  read: boolean,
}

export interface LinkedReference {
  id: number,
  reference: Reference,
  reference_id?: number,
}

export type ViewerTypeValue = typeof ViewerType[keyof typeof ViewerType]

export interface DeliverableViewSettings {
  viewerType: ViewerTypeValue,
  showPayment: boolean,
  showAddSubmission: boolean,
  showAddDeliverable: boolean,
  characterInitItems: Character[],
}

export interface LinkedSubmission {
  id: number,
  submission: Submission,
  submission_id?: number,
  display_position: number,
}

export interface NavSettings {
  drawer: boolean | null,
}

export interface NotificationSettings {
  bank_transfer_failed: Boolean,
  wait_list_updated: Boolean,
  renewal_failure: Boolean,
  order_update: Boolean,
  commission_slots_available: Boolean,
  new_comment__deliverable: Boolean,
  commissions_automatically_closed: Boolean,
  new_comment__conversation: Boolean,
  referral_landscape_credit: Boolean
}

export declare interface NotificationStats {
  count: number,
  community_count: number,
  sales_count: number,
}

export interface OrderProps {
  orderId: string | number,
  baseName: 'Order' | 'Sale' | 'Case',
}

export interface PaypalConfig {
  template_id: string,
  template_name: string,
  active: boolean,
}

export interface ServicePlan {
  id: number,
  name: string,
  description: string,
  features: string[],
  monthly_charge: string,
  waitlisting: boolean,
  paypal_invoicing: boolean,
  shield_static_price: string,
  per_deliverable_price: string,
  shield_percentage_price: string,
  max_simultaneous_orders: number,
}

export interface Pricing {
  plans: ServicePlan[],
  minimum_price: string,
  table_percentage: string,
  table_static: string,
  table_tax: string,
  international_conversion_percentage: string,
  preferred_plan: string,
}

export interface Product {
  id: number,
  name: string,
  description: string,
  details_template: string,
  revisions: number,
  hidden: boolean,
  max_parallel: number,
  max_rating: RatingsValue,
  hits: number,
  task_weight: number
  expected_turnaround: number,
  escrow_enabled: boolean,
  user: RelatedUser,
  base_price: string,
  starting_price: string,
  shield_price: string,
  tags: string[],
  available: boolean,
  featured: boolean,
  international: boolean,
  track_inventory: boolean,
  table_product: boolean,
  primary_submission: null | Submission,
  wait_list: boolean,
  catalog_enabled: boolean,
  cascade_fees: boolean,
  escrow_upgradable: boolean,
  display_position: number,
  over_order_limit: boolean,
  paypal: boolean,
  name_your_price: boolean,
}

export interface ProductProps {
  productId: number | string,
}

export interface Rating {
  id: number,
  stars: number,
  comments: string,
  rater: RelatedUser,
}

export interface RawLineItemSetMap {
  name: string,
  lineItems: LineItem[],
  offer: boolean,
}

export interface ReferralStats {
  total_referred: number,
  landscape_eligible: number,
}

export interface Revision {
  id: number,
  file: FileSpec,
  rating: RatingsValue,
  read: boolean,
  submissions: { owner_id: number, id: number }[],
  approved_on: string,
}

export interface ShoppingCart {
  product: number,
  email: string,
  private: boolean,
  details: string,
  characters: number[],
  rating: RatingsValue,
  references: number[],
  named_price: null | number,
  escrow_upgrade: boolean,
}

export type ConnectionStatusValue = typeof ConnectionStatus[keyof typeof ConnectionStatus]

export interface SocketState {
  status: ConnectionStatusValue,
  version: string,
  serverVersion: string,
}

export interface StripeAccount {
  id: string,
  active: boolean,
  country: string,
}

export interface StripeCountryList {
  countries: Array<{ title: string, value: string }>
}

export interface StripeReader {
  id: string,
  name: string,
}

export interface TabNavSpec {
  value: RouteLocationNamedRaw
  title: string,
  icon?: string,
  count?: number,
}

export interface TabSpec {
  value: number,
  title: string,
  icon?: string,
  count?: number,
}

export interface UserShare {
  user: TerseUser,
  id: number
}

export type AccountTypeValue = typeof AccountType[keyof typeof AccountType]

export type TransactionCategoryValue = typeof TransactionCategory[keyof typeof TransactionCategory]

export type TransactionStatusValue = typeof TransactionStatus[keyof typeof TransactionStatus]

export interface Transaction {
  id: string,
  source: AccountTypeValue,
  destination: AccountTypeValue,
  status: TransactionStatusValue,
  category: TransactionCategoryValue,
  card: CreditCardToken | null,
  payer: RelatedUser | null,
  payee: RelatedUser | null,
  amount: number,
  remote_id: string,
  created_on: string,
  response_message: '',
  finalized_on: string | null,
  targets: any[],
}

export interface TGDevice {
  id: number,
  confirmed: boolean,
  code?: number,
}

export interface TOTPDevice {
  id: number,
  name: string,
  config_url: string,
  confirmed: boolean,
  code?: string
}

export interface SocialSettings {
  id: number,
  allow_promotion: boolean,
  allow_site_promotion: boolean,
  nsfw_promotion: boolean,
  quick_description: string,
  promotion_notes: string,
  display_socials: boolean,
}

export interface SocialLink {
  id: number,
  url: string,
  site_name: string,
  identifier: string,
  comment: string,
}

export type LogLevelsValue = typeof LogLevels[keyof typeof LogLevels]
