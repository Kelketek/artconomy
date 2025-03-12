import { QueryParams } from "@/store/helpers/QueryParams.ts"

export default interface ListSocketSpec {
  appLabel: string
  modelName: string
  pk?: string
  listName: string
}

export interface ListSocketSettings {
  appLabel: string
  modelName: string
  keyField?: string
  serializer: string
  list: ListSocketSpec
}

export interface ListModuleOpts {
  grow?: boolean
  currentPage?: number
  endpoint: string
  reverse?: boolean
  prependNew?: boolean
  persistent?: boolean
  keyProp?: string
  paginated?: boolean
  stale?: boolean
  params?: QueryParams
  socketSettings?: ListSocketSettings | null
}

export interface PaginatedResponse {
  count: number
  size: number
}

export interface ListState<T> {
  response: PaginatedResponse | null
  refs: string[]
  grow: boolean
  endpoint: string
  persistent: boolean
  ready: boolean
  keyProp: keyof T
  // Needed for self-reference when constructing submodules.
  name: string
  fetching: boolean
  reverse: boolean
  prependNew: boolean
  failed: boolean
  paginated: boolean
  stale: boolean
  params: QueryParams
  socketSettings: ListSocketSettings | null
}
