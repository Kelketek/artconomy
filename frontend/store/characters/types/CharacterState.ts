import Color from '@/store/characters/types/Color'
import {ListState} from '@/store/lists/types/ListState'
import Submission from '@/types/Submission'
import {UserShare} from '@/types/UserShare'
import {SingleController} from '@/store/singles/controller'
import {Character} from '@/store/characters/types/Character'

export default interface CharacterState {
  profile?: SingleController<Character>
  colors?: ListState<Color>,
  submissions?: ListState<Submission>,
  sharedWith?: ListState<UserShare>,
  username: string,
  characterName: string,
  persistent: boolean,
}
