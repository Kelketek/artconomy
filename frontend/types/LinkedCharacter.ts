import {Character} from '@/store/characters/types/Character'

export default interface LinkedCharacter {
  id: number,
  character: Character,
  character_id?: number,
}
