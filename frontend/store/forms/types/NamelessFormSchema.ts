import {HttpVerbs} from '@/store/forms/types/HttpVerbs.ts'
import {FieldSetSchema} from '@/store/forms/types/FieldSetSchema.ts'

export interface NamelessFormSchema {
  endpoint: string,
  method?: HttpVerbs,
  fields: FieldSetSchema,
  errors?: string[],
  submitted?: boolean,
  disabled?: boolean,
  reset?: boolean,
  debounce?: number,
  // If set true, the formController will not be reaped when all references to it in the registry are removed.
  persistent?: boolean,
  step?: number,
}
