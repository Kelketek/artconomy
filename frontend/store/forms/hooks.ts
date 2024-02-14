import {ensureUnmountAction, generateModuleHooks, getUid, useRegistries, useRegistry} from '@/store/hooks.ts'
import {getController, performUnhook} from '@/store/registry-base.ts'
import {FormState} from '@/store/forms/types/FormState.ts'
import {FormController, RawFormController} from '@/store/forms/form-controller.ts'
import {useRouter} from 'vue-router'
import {useSocket} from '@/plugins/socket.ts'
import {useStore} from 'vuex'
import {NamelessFormSchema} from '@/store/forms/types/NamelessFormSchema.ts'

const {use, listen, clear} = generateModuleHooks<FormState, NamelessFormSchema, RawFormController>('Form', RawFormController)
export const useForm = (name: string, schema?: NamelessFormSchema) => use(name, schema) as FormController
export const listenForForm = listen
export const clearFormAssociations = clear
