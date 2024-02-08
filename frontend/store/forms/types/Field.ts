import {ValidatorSpec} from '@/store/forms/types/ValidatorSpec.ts'
import {RawData} from '@/store/forms/types/RawData.ts'

export interface Field {
  disabled: boolean,
  hidden: boolean,
  validators: ValidatorSpec[],
  value: any,
  errors: string[],
  initialData: any,
  extra: RawData,
  debounce: number | null,
  omitIf?: any
  step: number,
}
