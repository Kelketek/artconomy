import {QueryParams} from '@/store/helpers/QueryParams'

export interface ListModuleOpts {
  grow?: boolean,
  currentPage?: number,
  endpoint: string,
  pageSize?: number,
  reverse?: boolean,
  persistent?: boolean,
  keyProp?: string,
  paginated?: boolean,
  params?: QueryParams,
}
