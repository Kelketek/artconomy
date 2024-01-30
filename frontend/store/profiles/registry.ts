import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {ProfileController} from './controller'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts'
import {ProfileState} from '@/store/profiles/types/ProfileState'
import {ArtStore} from '@/store'

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
