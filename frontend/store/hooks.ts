import {getCurrentInstance, inject, markRaw, onUnmounted, provide} from 'vue'
import {ArtVueInterface} from '@/types/ArtVueInterface'
import {RegistryRegistry} from '@/store/registry-base'

export const useRegistry = <T extends 'Single'|'List'|'Form'|'Character'|'Profile'>(typeName: T, instance?: ArtVueInterface) => {
  const currentInstance = instance || (getCurrentInstance()?.appContext.app as null|ArtVueInterface)
  if (!currentInstance) {
    throw Error('Not in a Vue rendering environment!')
  }
  const registry = currentInstance[`$registryFor${typeName}`]()
  if (!registry) {
    throw Error(`Registry for ${typeName} not found. Is the plugin installed?`)
  }
  return registry as ReturnType<ArtVueInterface[`$registryFor${T}`]>
}

export const useRegistries = (): RegistryRegistry => {
  const app = getCurrentInstance()?.appContext.app as ArtVueInterface
  return markRaw({
    Single: useRegistry('Single', app),
    List: useRegistry('List', app),
    Form: useRegistry('Form', app),
    Character: useRegistry('Character', app),
    Profile: useRegistry('Profile', app),
  })
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
