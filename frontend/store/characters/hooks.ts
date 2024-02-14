import {generateModuleHooks} from '@/store/hooks.ts'

import CharacterState from '@/store/characters/types/CharacterState.ts'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts.ts'
import {CharacterController, RawCharacterController} from '@/store/characters/controller.ts'


const {use, listen, clear} = generateModuleHooks<CharacterState, CharacterModuleOpts, RawCharacterController>('Character', RawCharacterController)

export const useCharacter = (name: string, schema: CharacterModuleOpts) => use(name, schema) as CharacterController
export const listenForCharacter = listen
export const clearCharacterAssociations = clear
