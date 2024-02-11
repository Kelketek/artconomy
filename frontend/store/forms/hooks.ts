import {ensureUnmountAction, getUid, useRegistries, useRegistry} from '@/store/hooks.ts'
import {getController, performUnhook} from '@/store/registry-base.ts'
import {FormState} from '@/store/forms/types/FormState.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {useRouter} from 'vue-router'
import {useSocket} from '@/plugins/socket.ts'
import {useStore} from 'vuex'
import {NamelessFormSchema} from '@/store/forms/types/NamelessFormSchema.ts'

export const useForm = (name: string, schema?: NamelessFormSchema) => {
  const uid = getUid()
  const registries = useRegistries()
  const controller = getController<FormState, NamelessFormSchema, FormController>({
    uid,
    name,
    schema,
    typeName: 'List',
    router: useRouter(),
    socket: useSocket(),
    store: useStore(),
    registries,
    ControllerClass: FormController,
  })
  ensureUnmountAction('formUnmount', clearFormAssociations)
  return controller
}

export const listenForForm = (name: string) => {
  const uid = getUid()
  const registry = useRegistry('Form')
  registry.listen(uid, name)
  ensureUnmountAction('formUnmount', clearFormAssociations)
}


export const clearFormAssociations = () => {
  const uid = getUid()
  const registry = useRegistry('Form')
  performUnhook<FormState, NamelessFormSchema, FormController>(uid, registry)
}
