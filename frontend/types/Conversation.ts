import {TerseUser} from '@/store/profiles/types/TerseUser'
import {Comment} from '@/types/Comment'

export interface Conversation {
  id: number,
  read: boolean,
  participants: TerseUser[],
  created_on: string,
  last_comment: Comment|null,
}
