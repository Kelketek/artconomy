import {QueryParams} from '@/store/helpers/QueryParams.ts'
import {SingleSocketSettings} from '@/store/singles/types/SingleSocketSettings.ts'

export interface SingleModuleOpts<T> {
  x?: T | false | null,
  endpoint: string,
  persist?: boolean,
  attempted?: boolean,
  params?: QueryParams,
  socketSettings?: SingleSocketSettings|null,
}
