import FileSpec from '@/types/FileSpec.ts'
import {Ratings} from '@/types/Ratings.ts'

export default interface Reference {
  id: number,
  file: FileSpec,
  owner: string,
  rating: Ratings,
  created_on: string,
  read: boolean,
}
