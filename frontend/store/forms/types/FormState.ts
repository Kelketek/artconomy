import {FieldSet} from '@/store/forms/types/FieldSet.ts'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs.ts'

export interface FormState {
  fields: FieldSet,
  endpoint: string,
  method: HttpVerbs,
  errors: string[],
  submitted: boolean,
  disabled: boolean,
  reset: boolean,
  sending: boolean,
  persistent: boolean,
  step: number,
  debounce: number,
}
