import type FileSpec from '@/types/FileSpec.ts'
import type {RatingsValue} from '@/types/Ratings.ts'

export default interface Revision {
  id: number,
  file: FileSpec,
  rating: RatingsValue,
  read: boolean,
  submissions: {owner_id: number, id: number}[],
  approved_on: string,
}
