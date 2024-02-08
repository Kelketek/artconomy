import {TerseUser} from '@/store/profiles/types/TerseUser.ts'

export default interface Comment {
  id: number,
  text: string,
  user: TerseUser|null,
  created_on: string,
  edited: boolean,
  edited_on: string,
  deleted: boolean,
  comments: Comment[],
  comment_count: number,
  subscribed: boolean,
  system: boolean,
}
