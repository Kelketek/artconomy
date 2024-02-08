import {FormError} from '@/store/forms/types/FormError.ts'

export interface FormErrorSet {
  errors: string[],
  fields: FormError
}
