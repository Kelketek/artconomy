import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {RawCharacterController} from './controller.ts'
import CharacterState from '@/store/characters/types/CharacterState.ts'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts.ts'
import {ArtStore} from '@/store/index.ts'

export class CharacterRegistry extends BaseRegistry<CharacterState, RawCharacterController> {
}

export const characterRegistry = new CharacterRegistry('Controller')

export function createCharacters(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<CharacterState, CharacterModuleOpts, RawCharacterController>('Character', characterRegistry, RawCharacterController, store))
    }
  }
}

(window as any).characterRegistry = characterRegistry
