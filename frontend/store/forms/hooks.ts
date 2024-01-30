import {ensureUnmountAction, getUid, useRegistries, useRegistry} from '@/store/hooks'
import {getController, performUnhook} from '@/store/registry-base'
import {FormState} from '@/store/forms/types/FormState'
import {FormController} from '@/store/forms/form-controller'
import {useRouter} from 'vue-router'
import {useSocket} from '@/plugins/socket'
import {useStore} from 'vuex'
import {NamelessFormSchema} from '@/store/forms/types/NamelessFormSchema'

export const useForm = (name: string, schema: NamelessFormSchema) => {
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
