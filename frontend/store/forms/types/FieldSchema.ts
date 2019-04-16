import {ValidatorSpec} from '@/store/forms/types/ValidatorSpec'
import {RawData} from '@/store/forms/types/RawData'

export interface FieldSchema {
  disabled?: boolean,
  hidden?: boolean,
  validators?: ValidatorSpec[],
  value: any,
  errors?: string[],
  extra?: RawData,
  debounce?: number | null,
  omitIf?: any,
  step?: number,
}
