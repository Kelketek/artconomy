import {RelatedUser} from '@/store/profiles/types/RelatedUser'
import {Asset} from '@/types/Asset'
import {RawLocation} from 'vue-router'

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
  commission_link: RawLocation|null,
  comments_disabled: boolean,
}
