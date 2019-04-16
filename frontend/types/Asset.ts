import FileSpec from '@/types/FileSpec'
import {Ratings} from '@/store/profiles/types/Ratings'

export interface Asset {
  file: FileSpec,
  tags: string[],
  rating: Ratings,
  preview: FileSpec|null,
}
