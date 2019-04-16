import {User} from '@/store/profiles/types/User'
import {SingleState} from '@/store/singles/types/SingleState'
import {ArtistProfile} from '@/store/profiles/types/ArtistProfile'

export interface ProfileState {
  user?: SingleState<User>,
  artistProfile?: SingleState<ArtistProfile>,
  persistent: boolean,
  viewer: boolean,
}
