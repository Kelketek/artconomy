import {generateModuleHooks} from '@/store/hooks.ts'

import CharacterState from '@/store/characters/types/CharacterState.ts'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts.ts'
import {CharacterController} from '@/store/characters/controller.ts'
import {flatten} from '@/lib/lib.ts'


const {use, listen, clear} = generateModuleHooks<CharacterState, CharacterModuleOpts, CharacterController>('Character', CharacterController)

export const useCharacter = (schema: CharacterModuleOpts) => {
  return use(`character__${flatten(schema.username)}__${flatten(schema.characterName)}`, schema) as CharacterController
}
export const listenForCharacter = listen
export const clearCharacterAssociations = clear
