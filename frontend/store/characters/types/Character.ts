import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'
import type {Submission} from '@/types/main'

export interface Character {
  id: number,
  name: string,
  description: string,
  private: boolean,
  open_requests: boolean,
  open_requests_restrictions: string,
  user: RelatedUser,
  primary_submission: Submission|null,
  tags: string[],
  taggable: boolean,
  nsfw: boolean,
  hits: number,
}
