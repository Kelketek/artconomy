import {ComponentInternalInstance, getCurrentInstance, inject, onUnmounted, provide, reactive} from 'vue'
import {ArtVueInterface} from '@/types/ArtVueInterface.ts'
import {
  AttrKeys,
  getController,
  listenForRegistryName,
  ModuleName,
  performUnhook, Registry,
  RegistryRegistry,
} from '@/store/registry-base.ts'
import {buildRegistries} from '@/plugins/createRegistries.ts'
import {useSocket} from '@/plugins/socket.ts'
import {useStore} from 'vuex'
import {useRouter} from 'vue-router'
import {BaseController, ControllerArgs} from '@/store/controller-base.ts'

export type ArtVueInstance = ComponentInternalInstance & ArtVueInterface

export const guardedApp = (instance?: ArtVueInterface) => {
  const currentInstance = instance || getCurrentInstance()
  if (!currentInstance) {
    throw Error('Not in a rendering context!')
  }
  return currentInstance
}

export const useRegistry = <T extends 'Single'|'List'|'Form'|'Character'|'Profile'>(typeName: T) => {
  return useRegistries()[typeName]
}

export const useRegistries = (): RegistryRegistry => {
  return inject('$registries', buildRegistries, true)
}

export const getUid = () => {
  const app = getCurrentInstance()
  if (!app) {
    throw Error('Cannot provision UIDs without being in an active app environment.')
  }
  return `${app.uid}`
}

export const ensureUnmountAction = (key: string, func: () => any) => {
  const uid = getUid()
  const unmountKey = `ensureUnmount.${uid}.${key}`
  const marked = inject(unmountKey, false)
  if (!marked) {
    provide(unmountKey, true)
    onUnmounted(func)
  }
}

export const generateModuleHooks = <K extends AttrKeys, S, C extends BaseController<S, K>>(typeName: ModuleName, ControllerClass: new (args: ControllerArgs<S>) => C) => {
  const use = (name: string, schema?: S) => {
    const controller = getController<K, S, C>({
      name,
      schema,
      uid: getUid(),
      socket: useSocket(),
      typeName: typeName,
      store: useStore(),
      router: useRouter(),
      registries: useRegistries(),
      ControllerClass,
    })
    ensureUnmountAction(`${typeName}Unmount`, clear)
    return controller
  }
  const listen = (name: string) => {
    const uid = getUid()
    const registry = useRegistry(typeName) as unknown as Registry<K, C>
    registry.listen(uid, name)
    listenForRegistryName<K, S, C>(uid, name, registry)
    ensureUnmountAction(`${typeName}Unmount`, clear)
  }
  const clear = () => {
    const uid = getUid()
    const registry = useRegistry(typeName) as unknown as Registry<K, C>
    performUnhook<K, S, C>(uid, registry)
  }
  return {
    use,
    listen,
    clear,
  }
}
