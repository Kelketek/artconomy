import { RelatedUser } from "@/store/profiles/types/main"
import type { Submission, UserShare } from "@/types/main"
import { SingleController } from "@/store/singles/controller.ts"
import type { ListState } from "@/store/lists/types"

export interface Character {
  id: number
  name: string
  description: string
  private: boolean
  open_requests: boolean
  open_requests_restrictions: string
  user: RelatedUser
  primary_submission: Submission | null
  tags: string[]
  taggable: boolean
  nsfw: boolean
  hits: number
}

export interface CharacterModuleOpts {
  persistent?: boolean
  username: string
  characterName: string
}

export interface Color {
  id: number
  color: string
  note: string
}

export interface CharacterState {
  profile?: SingleController<Character>
  colors?: ListState<Color>
  submissions?: ListState<Submission>
  sharedWith?: ListState<UserShare>
  username: string
  characterName: string
  persistent: boolean
}
