import {Patch} from '@/store/singles/patcher.ts'

export type SinglePatchers<T> = {
  [Property in keyof T]: Patch<T[Property]>
}
