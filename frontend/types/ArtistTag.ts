import Submission from '@/types/Submission'

export default interface ArtistTag {
  submission: Submission,
  hidden: boolean,
  display_position: number,
  user: number,
}