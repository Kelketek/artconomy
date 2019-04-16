import {PaginatedResponse} from '@/store/lists/types/PaginatedResponse'
import {QueryParams} from '@/store/helpers/QueryParams'

export interface ListState<T> {
  response: PaginatedResponse | null,
  refs: string[],
  grow: boolean,
  currentPage: number,
  endpoint: string,
  pageSize: number,
  persistent: boolean,
  ready: boolean,
  keyProp: keyof T,
  // Needed for self-reference when constructing submodules.
  name: string,
  fetching: boolean,
  reverse: boolean,
  failed: boolean,
  paginated: boolean,
  params: QueryParams|null,
}
