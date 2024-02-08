import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'

export default interface Rating {
  id: number,
  stars: number,
  comments: string,
  rater: RelatedUser,
}
