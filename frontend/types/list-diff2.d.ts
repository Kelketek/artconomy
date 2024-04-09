declare module 'list-diff.js' {
  export type DiffPatch<T> = {
    index: number,
    type: 0,
  } | {
    index: number,
    type: 1,
    item: T,
  }
  export const DELETION = 0
  export const INSERTION = 1
  export const SUBSTITUTION = 2
  export default function diff <T>(a: T[], b: T[]): DiffPatch<T>[]
}
