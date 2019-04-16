import {QueryParams} from '@/store/helpers/QueryParams'

export interface SingleModuleOpts<T> {
  x?: T | false | null,
  endpoint: string,
  persist?: boolean,
  attempted?: boolean,
  params?: QueryParams,
}
