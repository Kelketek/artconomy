import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'
import {Asset} from '@/types/Asset.ts'
import {RouteLocationRaw} from 'vue-router'
import {Ratings} from '@/types/Ratings.ts'

export default interface Submission extends Asset {
  id: number,
  title: string,
  caption: string,
  private: boolean,
  created_on: string,
  owner: RelatedUser,
  comment_count: number,
  favorite_count: number,
  rating: Ratings,
  tags: string[],
  favorites: boolean,
  subscribed: boolean,
  hits: number,
  display_position: number,
  commission_link: RouteLocationRaw|null,
  comments_disabled: boolean,
  order: {order_id: number, deliverable_id: number}|null,
}
