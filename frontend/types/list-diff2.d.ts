declare module 'list-diff.js' {
  export type DiffPatch<T> = {
    index: number,
    type: 0,
  } | {
    index: number,
    type: 1,
    item: T,
  }
  export default function diff <T>(a: T[], b: T[]): DiffPatch<T>[]
}