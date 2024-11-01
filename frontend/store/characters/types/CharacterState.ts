import Color from '@/store/characters/types/Color.ts'
import {ListState} from '@/store/lists/types/ListState.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {Character} from '@/store/characters/types/Character.ts'
import type {Submission, UserShare} from '@/types/main'

export default interface CharacterState {
  profile?: SingleController<Character>
  colors?: ListState<Color>,
  submissions?: ListState<Submission>,
  sharedWith?: ListState<UserShare>,
  username: string,
  characterName: string,
  persistent: boolean,
}
