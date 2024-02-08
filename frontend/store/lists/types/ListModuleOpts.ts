import {QueryParams} from '@/store/helpers/QueryParams.ts'
import {ListSocketSettings} from '@/store/lists/types/ListSocketSettings.ts'

export interface ListModuleOpts {
  grow?: boolean,
  currentPage?: number,
  endpoint: string,
  reverse?: boolean,
  persistent?: boolean,
  keyProp?: string,
  paginated?: boolean,
  stale?: boolean,
  params?: QueryParams,
  socketSettings?: ListSocketSettings|null,
}
