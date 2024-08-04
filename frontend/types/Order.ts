import {User} from '@/store/profiles/types/User.ts'
import {RouteLocationNamedRaw} from 'vue-router'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import {Asset} from '@/types/Asset.ts'

export default interface Order {
  id: number,
  created_on: string,
  seller: User,
  buyer: User|null,
  customer_email: string,
  customer_display_name: string,
  // This one's read only, available on the preview serializer to help sellers pick out guest users.
  guest_email: string,
  private: boolean,
  hide_details: boolean,
  claim_token: string|null,
  product_name: string,
  display: Asset|null,
  default_path: RouteLocationNamedRaw,
  deliverable_count: number,
  status: DeliverableStatus,
  read: boolean,
}
