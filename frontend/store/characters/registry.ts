import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {CharacterController} from './controller'
import CharacterState from '@/store/characters/types/CharacterState'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts'
import {ArtStore} from '@/store'

export class CharacterRegistry extends BaseRegistry<CharacterState, CharacterController> {
}

export const characterRegistry = new CharacterRegistry('Controller')

export function createCharacters(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<CharacterState, CharacterModuleOpts, CharacterController>('Character', characterRegistry, CharacterController, store))
    }
  }
}

(window as any).characterRegistry = characterRegistry
