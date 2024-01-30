import {SingleModuleOpts} from '@/store/singles/types/SingleModuleOpts'
import {ensureUnmountAction, getUid, useRegistries, useRegistry} from '@/store/hooks'
import {getController, listenForRegistryName, performUnhook} from '@/store/registry-base'
import {SingleController} from '@/store/singles/controller'
import {SingleState} from '@/store/singles/types/SingleState'
import {useRouter} from 'vue-router'
import {useSocket} from '@/plugins/socket'
import {useStore} from 'vuex'

export const useSingle = <T extends object>(name: string, schema?: SingleModuleOpts<T>) => {
  const uid = getUid()
  const registries = useRegistries()
  const socket = useSocket()
  const controller = getController<SingleState<T>, SingleModuleOpts<T>, SingleController<T>>({
    uid,
    name,
    schema,
    registries,
    socket: socket,
    store: useStore(),
    typeName: 'Single',
    router: useRouter(),
    ControllerClass: SingleController,
  })
  ensureUnmountAction('singleUnmount', clearSingleAssociations)
  return controller
}

export const listenForSingle = <T extends object>(name: string) => {
  const uid = getUid()
  const registry = useRegistry('Single')
  registry.listen(uid, name)
  listenForRegistryName<SingleState<T>, SingleModuleOpts<T>, SingleController<T>>(uid, name, registry)
  ensureUnmountAction('singleUnmount', clearSingleAssociations)
}

// Must be called by every component that runs the above on unmount. Need to figure out how to automate this atomically.
export const clearSingleAssociations = () => {
  const uid = getUid()
  const registry = useRegistry('Single')
  performUnhook<SingleState<any>, SingleModuleOpts<any>, SingleController<any>>(uid, registry)
}
