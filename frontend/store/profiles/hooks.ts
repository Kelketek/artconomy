import {ensureUnmountAction, getUid, useRegistries, useRegistry} from '@/store/hooks.ts'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts.ts'
import {ProfileRegistry} from '@/store/profiles/registry.ts'
import {getController, performUnhook} from '@/store/registry-base.ts'
import {ProfileState} from '@/store/profiles/types/ProfileState.ts'
import {ProfileController} from '@/store/profiles/controller.ts'
import {useRouter} from 'vue-router'
import {useSocket} from '@/plugins/socket.ts'
import {useStore} from 'vuex'

export const useProfile = (name: string, schema: ProfileModuleOpts = {}) => {
  const uid = getUid()
  const registries = useRegistries()
  const controller = getController<ProfileState, ProfileModuleOpts, ProfileController>({
    uid,
    name,
    schema,
    typeName: 'Profile',
    router: useRouter(),
    socket: useSocket(),
    store: useStore(),
    registries,
    ControllerClass: ProfileController,
  })
  ensureUnmountAction('profileUnmount', clearProfileAssociations)
  return controller
}

export const listenForProfile = (name: string) => {
  const uid = getUid()
  const registry = useRegistry('Profile') as ProfileRegistry
  registry.listen(uid, name)
  ensureUnmountAction('profileUnmount', clearProfileAssociations)
}

export const clearProfileAssociations = () => {
  const uid = getUid()
  const registry = useRegistry('Profile')
  performUnhook<ProfileState, ProfileModuleOpts, ProfileController>(uid, registry)
}
