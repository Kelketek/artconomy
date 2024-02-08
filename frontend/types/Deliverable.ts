import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import Product from '@/types/Product.ts'
import {User} from '@/store/profiles/types/User.ts'
import Submission from '@/types/Submission.ts'
import {Ratings} from '@/store/profiles/types/Ratings.ts'
import FileSpec from '@/types/FileSpec.ts'
import Order from '@/types/Order.ts'
import {PROCESSORS} from '@/types/PROCESSORS.ts'

export default interface Deliverable {
  id: number,
  name: string,
  created_on: string,
  status: DeliverableStatus,
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
  rating: Ratings,
  processor: PROCESSORS,
  display: {file: FileSpec, preview: FileSpec|null}|null,
  order: Order,
  invoice: string | null,
  tip_invoice: string | null,
  read: boolean,
  cascade_fees: boolean,
  paypal: boolean,
  paypal_token: string,
  notes: string,
}
