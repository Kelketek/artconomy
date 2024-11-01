import {generateModuleHooks} from '@/store/hooks.ts'
import {FormController} from '@/store/forms/form-controller.ts'

import {FormState, NamelessFormSchema} from '@/store/forms/types/main'

const {use, listen, clear} = generateModuleHooks<FormState, NamelessFormSchema, FormController>('Form', FormController)
export const useForm = (name: string, schema?: NamelessFormSchema) => use(name, schema) as FormController
export const listenForForm = listen
export const clearFormAssociations = clear
