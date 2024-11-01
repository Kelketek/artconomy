import {createApp, markRaw} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {ProfileController} from './controller.ts'
import {ArtStore} from '@/store/index.ts'
import {ProfileModuleOpts, ProfileState} from '@/store/profiles/types/main'

export class ProfileRegistry extends BaseRegistry<ProfileState, ProfileController> {}

export const profileRegistry = markRaw(new ProfileRegistry('Profile'))

export function createProfiles(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<ProfileState, ProfileModuleOpts, ProfileController>('Profile', profileRegistry, ProfileController, store))
    }
  }
}

(window as any).profileRegistry = profileRegistry
