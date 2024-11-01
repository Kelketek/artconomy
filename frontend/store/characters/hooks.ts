import {generateModuleHooks} from '@/store/hooks.ts'

import {CharacterController} from '@/store/characters/controller.ts'
import {flatten} from '@/lib/lib.ts'
import type {CharacterModuleOpts, CharacterState} from '@/store/characters/types/main'


const {use, listen, clear} = generateModuleHooks<CharacterState, CharacterModuleOpts, CharacterController>('Character', CharacterController)

export const useCharacter = (schema: CharacterModuleOpts) => {
  return use(`character__${flatten(schema.username)}__${flatten(schema.characterName)}`, schema) as CharacterController
}
export const listenForCharacter = listen
export const clearCharacterAssociations = clear
