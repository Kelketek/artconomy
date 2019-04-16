import _Vue from 'vue'
import {genRegistryBase, genRegistryPluginBase, Registry} from '../registry-base'
import {ProfileController} from './controller'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts'
import {ProfileState} from '@/store/profiles/types/ProfileState'

declare interface ProfileRegistry extends Registry<ProfileState, ProfileController> {
}

export const profileRegistry = new _Vue(genRegistryBase()) as ProfileRegistry

export function Profiles(Vue: typeof _Vue): void {
  Vue.mixin(genRegistryPluginBase('Profile', profileRegistry, ProfileController))
}

declare module 'vue/types/vue' {
  // Global properties can be declared
  // on the `VueConstructor` interface

  interface Vue {
    $getProfile: (name: string, schema?: ProfileModuleOpts) => ProfileController,
    $listenForProfile: (name: string) => void,
  }
}

(window as any).profileRegistry = profileRegistry
