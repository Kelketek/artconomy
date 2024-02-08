import {QueryParams} from '@/store/helpers/QueryParams.ts'
import {SingleSocketSettings} from '@/store/singles/types/SingleSocketSettings.ts'

export interface SingleState<T> {
  x: null | T,
  endpoint: string,
  persistent: boolean,
  fetching: boolean,
  ready: boolean,
  failed: boolean,
  deleted: boolean,
  params: QueryParams|null,
  socketSettings: SingleSocketSettings|null,
}
