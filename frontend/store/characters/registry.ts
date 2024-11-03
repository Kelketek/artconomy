import {createApp, markRaw} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {CharacterController} from './controller.ts'
import {ArtStore} from '@/store/index.ts'
import {CharacterModuleOpts, CharacterState} from '@/store/characters/types/main'

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
