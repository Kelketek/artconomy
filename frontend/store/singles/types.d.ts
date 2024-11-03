import {QueryParams} from '@/store/helpers/QueryParams.ts'
import {Patch} from '@/store/singles/patcher.ts'

export default interface Proxy<T> {
  get(): T;

  set(value: T): void;
}

export interface SingleSocketSettings {
  appLabel: string,
  modelName: string,
  keyField?: string,
  serializer: string,
}

export interface SingleModuleOpts<T> {
  x?: T | false | null,
  endpoint: string,
  persist?: boolean,
  attempted?: boolean,
  params?: QueryParams,
  socketSettings?: SingleSocketSettings | null,
}

export type SinglePatchers<T> = {
  [Property in keyof T]: Patch<T[Property]>
}

export interface SingleState<T> {
  x: null | T,
  endpoint: string,
  persistent: boolean,
  fetching: boolean,
  ready: boolean,
  failed: boolean,
  deleted: boolean,
  params: QueryParams | null,
  socketSettings: SingleSocketSettings | null,
}
