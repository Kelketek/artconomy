import {QueryParams} from '@/store/helpers/QueryParams'
import {ListSocketSettings} from '@/store/lists/types/ListSocketSettings'

export interface ListModuleOpts {
  grow?: boolean,
  currentPage?: number,
  endpoint: string,
  pageSize?: number,
  reverse?: boolean,
  persistent?: boolean,
  keyProp?: string,
  paginated?: boolean,
  stale?: boolean,
  params?: QueryParams,
  socketSettings?: ListSocketSettings|null,
}
