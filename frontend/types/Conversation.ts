import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import Comment from '@/types/Comment.ts'

export interface Conversation {
  id: number,
  read: boolean,
  participants: TerseUser[],
  created_on: string,
  last_comment: Comment|null,
}
