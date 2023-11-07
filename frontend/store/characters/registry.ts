import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {CharacterController} from './controller'
import CharacterState from '@/store/characters/types/CharacterState'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts'

export class CharacterRegistry extends BaseRegistry<CharacterState, CharacterController> {
}

export const characterRegistry = new CharacterRegistry()

export function Characters(Vue: ReturnType<typeof createApp>): void {
  Vue.mixin(genRegistryPluginBase<CharacterState, CharacterModuleOpts, CharacterController>('Character', characterRegistry, CharacterController))
}

(window as any).characterRegistry = characterRegistry
