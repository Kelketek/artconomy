import {ValidatorSpec} from '@/store/forms/types/ValidatorSpec'
import {RawData} from '@/store/forms/types/RawData'

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
