import {PaginatedResponse} from '@/store/lists/types/PaginatedResponse'
import {QueryParams} from '@/store/helpers/QueryParams'
import {ListSocketSettings} from '@/store/lists/types/ListSocketSettings'

export interface ListState<T> {
  response: PaginatedResponse | null,
  refs: string[],
  grow: boolean,
  endpoint: string,
  persistent: boolean,
  ready: boolean,
  keyProp: keyof T,
  // Needed for self-reference when constructing submodules.
  name: string,
  fetching: boolean,
  reverse: boolean,
  failed: boolean,
  paginated: boolean,
  stale: boolean,
  params: QueryParams|null,
  socketSettings: ListSocketSettings|null,
}
