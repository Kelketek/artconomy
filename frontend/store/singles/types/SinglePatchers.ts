import {Patch} from '@/store/singles/patcher'

export type SinglePatchers<T> = Record<keyof T, Patch>
