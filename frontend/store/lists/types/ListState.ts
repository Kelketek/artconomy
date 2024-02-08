import {PaginatedResponse} from '@/store/lists/types/PaginatedResponse.ts'
import {QueryParams} from '@/store/helpers/QueryParams.ts'
import {ListSocketSettings} from '@/store/lists/types/ListSocketSettings.ts'

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
  params: QueryParams,
  socketSettings: ListSocketSettings|null,
}
