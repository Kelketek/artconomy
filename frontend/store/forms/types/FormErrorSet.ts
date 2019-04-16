import {FormError} from '@/store/forms/types/FormError'

export interface FormErrorSet {
  errors: string[],
  fields: FormError
}
