import {QueryParams} from '@/store/helpers/QueryParams'

export interface SingleState<T> {
  x: null | false | T,
  endpoint: string,
  persistent: boolean,
  fetching: boolean,
  ready: boolean,
  failed: boolean,
  params: QueryParams|null,
}
