import Submission from '@/types/Submission'
import {RelatedUser} from '@/store/profiles/types/RelatedUser'

export default interface ArtistTag {
  id: number,
  submission: Submission,
  hidden: boolean,
  display_position: number,
  user: RelatedUser,
}
