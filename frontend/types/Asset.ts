import FileSpec from '@/types/FileSpec.ts'
import {Ratings} from '@/store/profiles/types/Ratings.ts'

export interface Asset {
  file: FileSpec,
  tags?: string[],
  rating: Ratings,
  preview: FileSpec|null,
}
