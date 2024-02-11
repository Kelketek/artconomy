import {ListModuleOpts} from '@/store/lists/types/ListModuleOpts.ts'
import {ensureUnmountAction, getUid, useRegistries, useRegistry} from '@/store/hooks.ts'
import {getController, performUnhook} from '@/store/registry-base.ts'
import {ListState} from '@/store/lists/types/ListState.ts'
import {ListController} from '@/store/lists/controller.ts'
import {useRouter} from 'vue-router'
import {useSocket} from '@/plugins/socket.ts'
import {useStore} from 'vuex'

export const useList = <T extends object>(name: string, schema?: ListModuleOpts) => {
  const uid = getUid()
  const registries = useRegistries()
  const controller = getController<ListState<T>, ListModuleOpts, ListController<T>>({
    uid,
    name,
    schema,
    typeName: 'List',
    router: useRouter(),
    socket: useSocket(),
    store: useStore(),
    registries,
    ControllerClass: ListController,
  })
  ensureUnmountAction('listUnmount', clearListAssociations)
  return controller
}

export const listenForList = (name: string) => {
  const uid = getUid()
  const registry = useRegistry('List')
  registry.listen(uid, name)
  ensureUnmountAction('listUnmount', clearListAssociations)
}


export const clearListAssociations = () => {
  const uid = getUid()
  const registry = useRegistry('List')
  performUnhook<ListState<any>, ListModuleOpts, ListController<any>>(uid, registry)
}
