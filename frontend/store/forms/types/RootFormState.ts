import {FormState} from '@/store/forms/types/FormState.ts'

export interface RootFormState {
  [key: string]: FormState,
}
