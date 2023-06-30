import {RelatedUser} from '@/store/profiles/types/RelatedUser'
import Submission from '@/types/Submission'
import {Ratings} from '@/store/profiles/types/Ratings'

export default interface Product {
  id: number,
  name: string,
  description: string,
  revisions: number,
  hidden: boolean,
  max_parallel: number,
  max_rating: Ratings,
  task_weight: number
  expected_turnaround: number,
  escrow_enabled: boolean,
  user: RelatedUser,
  base_price: number,
  starting_price: number,
  shield_price: number,
  tags: string[],
  available: boolean,
  featured: boolean,
  international: boolean,
  track_inventory: boolean,
  table_product: boolean,
  primary_submission: null|Submission,
  wait_list: boolean,
  catalog_enabled: boolean,
  cascade_fees: boolean,
  escrow_upgradable: boolean,
  display_position: number,
  over_order_limit: boolean,
  paypal: boolean,
}
