import {ComponentInternalInstance, getCurrentInstance, inject, onUnmounted, provide} from 'vue'
import {ArtVueInterface} from '@/types/ArtVueInterface.ts'
import {RegistryRegistry} from '@/store/registry-base.ts'
import {buildRegistries} from '@/plugins/createRegistries.ts'

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
