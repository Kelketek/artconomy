import Color from '@/store/characters/types/Color.ts'
import {ListState} from '@/store/lists/types/ListState.ts'
import Submission from '@/types/Submission.ts'
import {UserShare} from '@/types/UserShare.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {Character} from '@/store/characters/types/Character.ts'

export default interface CharacterState {
  profile?: SingleController<Character>
  colors?: ListState<Color>,
  submissions?: ListState<Submission>,
  sharedWith?: ListState<UserShare>,
  username: string,
  characterName: string,
  persistent: boolean,
}
