import {RelatedUser} from '@/store/profiles/types/RelatedUser'
import Submission from '@/types/Submission'

export default interface Product {
  id: number,
  name: string,
  description: string,
  revisions: number,
  hidden: boolean,
  max_parallel: number,
  task_weight: number
  expected_turnaround: number,
  escrow_disabled: boolean,
  user: RelatedUser,
  base_price: number,
  starting_price: number,
  tags: string[],
  available: boolean,
  featured: boolean,
  track_inventory: boolean,
  table_product: boolean,
  primary_submission: null|Submission,
  wait_list: boolean,
  catalog_enabled: boolean,
}
