import {User} from '@/store/profiles/types/User.ts'
import {SingleState} from '@/store/singles/types/SingleState.ts'
import {ArtistProfile} from '@/store/profiles/types/ArtistProfile.ts'

export interface ProfileState {
  user?: SingleState<User>,
  artistProfile?: SingleState<ArtistProfile>,
  persistent: boolean,
  viewer: boolean,
}
