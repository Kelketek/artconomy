import {ensureUnmountAction, getUid, useRegistries, useRegistry} from '@/store/hooks.ts'
import {getController, performUnhook} from '@/store/registry-base.ts'
import CharacterState from '@/store/characters/types/CharacterState.ts'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts.ts'
import {CharacterController} from '@/store/characters/controller.ts'
import {useRouter} from 'vue-router'
import {useSocket} from '@/plugins/socket.ts'
import {useStore} from 'vuex'

export const useCharacter = (name: string, schema: CharacterModuleOpts) => {
  const uid = getUid()
  const registries = useRegistries()
  const controller = getController<CharacterState, CharacterModuleOpts, CharacterController>({
    uid,
    name,
    schema,
    typeName: 'List',
    router: useRouter(),
    socket: useSocket(),
    store: useStore(),
    registries,
    ControllerClass: CharacterController,
  })
  ensureUnmountAction('characterUnmount', clearCharacterAssociations)
  return controller
}

export const listenForList = (name: string) => {
  const uid = getUid()
  const registry = useRegistry('List')
  registry.listen(uid, name)
  ensureUnmountAction('listUnmount', clearCharacterAssociations)
}

export const clearCharacterAssociations = () => {
  const uid = getUid()
  const registry = useRegistry('Character')
  performUnhook<CharacterState, CharacterModuleOpts, CharacterController>(uid, registry)
}
