import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base.ts'
import {RawProfileController} from './controller.ts'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts.ts'
import {ProfileState} from '@/store/profiles/types/ProfileState.ts'
import {ArtStore} from '@/store/index.ts'

export class ProfileRegistry extends BaseRegistry<ProfileState, RawProfileController> {}

export const profileRegistry = new ProfileRegistry('Profile')

export function createProfiles(store: ArtStore) {
  return {
    install(app: ReturnType<typeof createApp>) {
      app.mixin(genRegistryPluginBase<ProfileState, ProfileModuleOpts, RawProfileController>('Profile', profileRegistry, RawProfileController, store))
    }
  }
}

(window as any).profileRegistry = profileRegistry
