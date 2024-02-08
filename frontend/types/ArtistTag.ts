import Submission from '@/types/Submission.ts'
import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'

export default interface ArtistTag {
  id: number,
  submission: Submission,
  hidden: boolean,
  display_position: number,
  user: RelatedUser,
}
