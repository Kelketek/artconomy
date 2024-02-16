import {generateModuleHooks} from '@/store/hooks.ts'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts.ts'
import {ProfileState} from '@/store/profiles/types/ProfileState.ts'
import {ProfileController} from '@/store/profiles/controller.ts'

const {use, listen, clear} = generateModuleHooks<ProfileState, ProfileModuleOpts, ProfileController>('Profile', ProfileController)

export const useProfile = (name: string, schema: ProfileModuleOpts = {}) => use(name, schema) as ProfileController
export const listenForProfile = listen
export const clearProfileAssociations = clear
