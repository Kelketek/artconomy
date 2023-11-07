import {RelatedUser} from '@/store/profiles/types/RelatedUser'
import {Asset} from '@/types/Asset'
import {RouteLocationRaw} from 'vue-router'

export default interface Submission extends Asset {
  id: number,
  title: string,
  caption: string,
  private: boolean,
  created_on: string,
  owner: RelatedUser,
  comment_count: number,
  favorite_count: number,
  favorites: boolean,
  subscribed: boolean,
  hits: number,
  display_position: number,
  commission_link: RouteLocationRaw|null,
  comments_disabled: boolean,
  order: {order_id: number, deliverable_id: number}|null,
}
