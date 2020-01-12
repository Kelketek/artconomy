import {OrderStatus} from '@/types/OrderStatus'
import {User} from '@/store/profiles/types/User'
import Product from '@/types/Product'
import Submission from '@/types/Submission'
import FileSpec from '@/types/FileSpec'
import {Ratings} from '@/store/profiles/types/Ratings'

export default interface Order {
  id: number,
  created_on: string,
  status: OrderStatus,
  price: number,
  product: Product|null,
  details: string,
  commission_info: string,
  seller: User,
  buyer: User|null,
  customer_email: string,
  arbitrator: User|null,
  adjustment: number,
  stream_link: string,
  revisions: number,
  outputs: Submission[],
  private: boolean,
  subscribed: boolean,
  tip: number,
  adjustment_task_weight: number,
  adjustment_expected_turnaround: number,
  adjustment_revisions: number,
  expected_turnaround: number,
  task_weight: number,
  paid_on: null|string,
  dispute_available_on: null|string,
  auto_finalize_on: null|string,
  started_on: null|string,
  escrow_disabled: boolean,
  revisions_hidden: boolean,
  final_uploaded: boolean,
  claim_token: string|null,
  rating: Ratings,
  display: {file: FileSpec, preview: FileSpec|null}|null
}
