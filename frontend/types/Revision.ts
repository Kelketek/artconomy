import FileSpec from '@/types/FileSpec'
import {Ratings} from '@/store/profiles/types/Ratings'

export default interface Revision {
  id: number,
  file: FileSpec,
  rating: Ratings
}
