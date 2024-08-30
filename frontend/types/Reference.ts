import type FileSpec from '@/types/FileSpec.ts'
import type {RatingsValue} from '@/types/Ratings.ts'

export default interface Reference {
  id: number,
  file: FileSpec,
  owner: string,
  rating: RatingsValue,
  created_on: string,
  read: boolean,
}
