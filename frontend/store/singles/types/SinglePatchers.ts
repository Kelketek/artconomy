import {Patch} from '@/store/singles/patcher.ts'

export type SinglePatchers<T> = Record<keyof T, Patch>
