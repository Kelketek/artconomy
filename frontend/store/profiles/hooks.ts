import { generateModuleHooks } from "@/store/hooks.ts"
import { ProfileController } from "@/store/profiles/controller.ts"
import { ProfileModuleOpts, ProfileState } from "@/store/profiles/types/main"

const { use, listen, clear } = generateModuleHooks<
  ProfileState,
  ProfileModuleOpts,
  ProfileController
>("Profile", ProfileController)

export const useProfile = (name: string, schema: ProfileModuleOpts = {}) =>
  use(name, schema) as ProfileController
export const listenForProfile = listen
export const clearProfileAssociations = clear
