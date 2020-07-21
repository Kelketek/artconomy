import {User} from '@/store/profiles/types/User'
import FileSpec from '@/types/FileSpec'
import {Location} from 'vue-router'

export default interface Order {
  id: number,
  created_on: string,
  seller: User,
  buyer: User|null,
  customer_email: string,
  private: boolean,
  claim_token: string|null,
  product_name: string,
  display: {file: FileSpec, preview: FileSpec|null}|null,
  default_path: Location,
  deliverable_count: number,
  read: boolean,
}
