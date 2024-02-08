import FileSpec from '@/types/FileSpec.ts'

export default interface Reference {
  id: number,
  file: FileSpec,
  owner: string,
  rating: number,
  created_on: string,
  read: boolean,
}
