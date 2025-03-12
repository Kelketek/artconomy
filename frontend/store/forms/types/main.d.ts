import { MetaToggles } from "@/store/forms/types/enums/MetaToggles.ts"

export interface RawData {
  [key: string]: any
}

export interface ValidatorSpec {
  name: string
  args?: any[]
  async?: boolean
}

export interface Field {
  disabled: boolean
  hidden: boolean
  validators: ValidatorSpec[]
  value: any
  errors: string[]
  initialData: any
  extra: RawData
  debounce: number | null
  omitIf?: any
  step: number
}

export interface FieldSchema {
  disabled?: boolean
  hidden?: boolean
  validators?: ValidatorSpec[]
  value: any
  errors?: string[]
  extra?: RawData
  debounce?: number | null
  omitIf?: any
  step?: number
}

export interface FieldSet {
  [key: string]: Field
}

export interface FieldSetSchema {
  [key: string]: FieldSchema
}

export interface FormError {
  [key: string]: string[]
}

export interface FormErrorSet {
  errors: string[]
  fields: FormError
}

export type HttpVerbs = "get" | "post" | "put" | "patch" | "delete"

export interface NamelessFormSchema {
  endpoint: string
  method?: HttpVerbs
  fields: FieldSetSchema
  errors?: string[]
  submitted?: boolean
  disabled?: boolean
  reset?: boolean
  debounce?: number
  // If set true, the formController will not be reaped when all references to it in the registry are removed.
  persistent?: boolean
  step?: number
}

export interface FormSchema extends NamelessFormSchema {
  name: string
}

export interface FormState {
  fields: FieldSet
  endpoint: string
  method: HttpVerbs
  errors: string[]
  submitted: boolean
  disabled: boolean
  reset: boolean
  sending: boolean
  persistent: boolean
  step: number
  debounce: number
}

export type MetaTogglesValue = (typeof MetaToggles)[keyof typeof MetaToggles]

export interface RootFormState {
  [key: string]: FormState
}

export default interface StepSpec {
  failed: boolean
  complete: boolean
  rules: Array<() => boolean>
}
