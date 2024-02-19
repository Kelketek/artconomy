import {createApp, markRaw} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {CharacterController} from './controller.ts'
import CharacterState from '@/store/characters/types/CharacterState.ts'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts.ts'
import {ArtStore} from '@/store/index.ts'

export class CharacterRegistry extends BaseRegistry<CharacterState, CharacterController> {
}

export const characterRegistry = markRaw(new CharacterRegistry('Controller'))

export function createCharacters(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<CharacterState, CharacterModuleOpts, CharacterController>('Character', characterRegistry, CharacterController, store))
    }
  }
}

(window as any).characterRegistry = characterRegistry
