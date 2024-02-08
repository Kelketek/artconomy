import {NamelessFormSchema} from './NamelessFormSchema.ts'

export interface FormSchema extends NamelessFormSchema {
  name: string,
}
