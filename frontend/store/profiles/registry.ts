import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {ProfileController} from './controller.ts'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts.ts'
import {ProfileState} from '@/store/profiles/types/ProfileState.ts'
import {ArtStore} from '@/store/index.ts'

export class ProfileRegistry extends BaseRegistry<ProfileState, ProfileController> {}

export const profileRegistry = new ProfileRegistry('Profile')

export function createProfiles(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<ProfileState, ProfileModuleOpts, ProfileController>('Profile', profileRegistry, ProfileController, store))
    }
  }
}

(window as any).profileRegistry = profileRegistry
