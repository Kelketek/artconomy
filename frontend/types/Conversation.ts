import {TerseUser} from '@/store/profiles/types/TerseUser'
import {User} from '@/store/profiles/types/User'

export interface Conversation {
  id: number,
  read: boolean,
  participants: TerseUser[],
}
