import {generateModuleHooks} from '@/store/hooks.ts'
import {FormState} from '@/store/forms/types/FormState.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {NamelessFormSchema} from '@/store/forms/types/NamelessFormSchema.ts'

const {use, listen, clear} = generateModuleHooks<FormState, NamelessFormSchema, FormController>('Form', FormController)
export const useForm = (name: string, schema?: NamelessFormSchema) => use(name, schema) as FormController
export const listenForForm = listen
export const clearFormAssociations = clear
