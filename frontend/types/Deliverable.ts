import type {DeliverableStatusValue} from '@/types/DeliverableStatus.ts'
import type Product from '@/types/Product.ts'
import type {User} from '@/store/profiles/types/User.ts'
import type Submission from '@/types/Submission.ts'
import type {RatingsValue} from '@/types/Ratings.ts'
import type Order from '@/types/Order.ts'
import type {Asset} from '@/types/Asset.ts'

export default interface Deliverable {
  id: number,
  name: string,
  created_on: string,
  status: DeliverableStatusValue,
  product: Product|null,
  price: number,
  details: string,
  commission_info: string,
  arbitrator: User|null,
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
  paid_on: null|string,
  trust_finalized: boolean,
  dispute_available_on: null|string,
  auto_finalize_on: null|string,
  started_on: null|string,
  escrow_enabled: boolean,
  revisions_hidden: boolean,
  table_order: boolean,
  international: boolean,
  final_uploaded: boolean,
  rating: RatingsValue,
  display: Asset|null,
  order: Order,
  invoice: string | null,
  tip_invoice: string | null,
  read: boolean,
  cascade_fees: boolean,
  paypal: boolean,
  paypal_token: string,
  notes: string,
}
