import {createApp} from 'vue'
import {BaseRegistry, genRegistryPluginBase} from '../registry-base'
import {ProfileController} from './controller'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts'
import {ProfileState} from '@/store/profiles/types/ProfileState'

export class ProfileRegistry extends BaseRegistry<ProfileState, ProfileController> {}

export const profileRegistry = new ProfileRegistry()

export function Profiles(app: ReturnType<typeof createApp>): void {
  app.mixin(genRegistryPluginBase<ProfileState, ProfileModuleOpts, ProfileController>('Profile', profileRegistry, ProfileController))
}

(window as any).profileRegistry = profileRegistry
