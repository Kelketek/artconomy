import {DeliverableStatus} from '@/types/DeliverableStatus'
import Product from '@/types/Product'
import {User} from '@/store/profiles/types/User'
import Submission from '@/types/Submission'
import {Ratings} from '@/store/profiles/types/Ratings'
import FileSpec from '@/types/FileSpec'
import Order from '@/types/Order'
import {PROCESSORS} from '@/types/PROCESSORS'

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
  escrow_disabled: boolean,
  revisions_hidden: boolean,
  table_order: boolean,
  final_uploaded: boolean,
  rating: Ratings,
  processor: PROCESSORS,
  display: {file: FileSpec, preview: FileSpec|null}|null,
  order: Order,
  invoice: string | null,
  read: boolean,
}
