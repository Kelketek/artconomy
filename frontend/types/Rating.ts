import {RelatedUser} from '@/store/profiles/types/RelatedUser'

export default interface Rating {
  id: number,
  stars: number,
  comments: string,
  rater: RelatedUser,
}
