import FileSpec from '@/types/FileSpec.ts'
import {Ratings} from '@/store/profiles/types/Ratings.ts'

export default interface Revision {
  id: number,
  file: FileSpec,
  rating: Ratings,
  read: boolean,
  submissions: {owner_id: number, id: number}[],
  approved_on: string,
}
