import {ValidatorSpec} from '@/store/forms/types/ValidatorSpec.ts'
import {RawData} from '@/store/forms/types/RawData.ts'

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
