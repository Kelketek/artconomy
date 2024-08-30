import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'
import Submission from '@/types/Submission.ts'
import {RatingsValue} from '@/types/Ratings.ts'

export default interface Product {
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
  primary_submission: null|Submission,
  wait_list: boolean,
  catalog_enabled: boolean,
  cascade_fees: boolean,
  escrow_upgradable: boolean,
  display_position: number,
  over_order_limit: boolean,
  paypal: boolean,
  name_your_price: boolean,
}
