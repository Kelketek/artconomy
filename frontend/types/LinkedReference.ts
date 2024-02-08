import Reference from '@/types/Reference.ts'

export default interface LinkedReference {
  id: number,
  reference: Reference,
  reference_id?: number,
}
