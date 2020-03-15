import FileSpec from '@/types/FileSpec'

export default interface Reference {
  id: number,
  file: FileSpec,
  owner: string,
  created_on: string,
}
