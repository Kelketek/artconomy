import {TerseUser} from '@/store/profiles/types/TerseUser'

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
}
