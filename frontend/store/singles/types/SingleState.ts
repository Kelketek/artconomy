import {QueryParams} from '@/store/helpers/QueryParams'
import {SingleSocketSettings} from '@/store/singles/types/SingleSocketSettings'

export interface SingleState<T> {
  x: null | T,
  endpoint: string,
  persistent: boolean,
  fetching: boolean,
  ready: boolean,
  failed: boolean,
  deleted: boolean,
  params: QueryParams|null,
  socketSettings?: SingleSocketSettings|null,
}
