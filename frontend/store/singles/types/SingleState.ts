import {QueryParams} from '@/store/helpers/QueryParams'
import {SingleSocketSettings} from '@/store/singles/types/SingleSocketSettings'

export interface SingleState<T> {
  x: null | false | T,
  endpoint: string,
  persistent: boolean,
  fetching: boolean,
  ready: boolean,
  failed: boolean,
  params: QueryParams|null,
  socketSettings?: SingleSocketSettings|null,
}
