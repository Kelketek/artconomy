import _Vue from 'vue'
import {genRegistryBase, genRegistryPluginBase, Registry} from '../registry-base'
import {CharacterController} from './controller'
import CharacterState from '@/store/characters/types/CharacterState'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts'

declare interface CharacterRegistry extends Registry<CharacterState, CharacterController> {
}

export const characterRegistry = new _Vue(genRegistryBase()) as CharacterRegistry

export function Characters(Vue: typeof _Vue): void {
  Vue.mixin(genRegistryPluginBase('Character', characterRegistry, CharacterController))
}

declare module 'vue/types/vue' {
  // Global properties can be declared
  // on the `VueConstructor` interface

  interface Vue {
    $getCharacter: (name: string, schema?: CharacterModuleOpts) => CharacterController,
  }
}

(window as any).characterRegistry = characterRegistry
