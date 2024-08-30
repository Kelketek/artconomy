import FileSpec from '@/types/FileSpec.ts'
import {Ratings, RatingsValue} from '@/types/Ratings.ts'

export interface Asset {
  file: FileSpec,
  tags?: string[],
  rating: RatingsValue,
  preview?: FileSpec|null,
}
