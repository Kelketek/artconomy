import {ProfileState} from '@/store/profiles/types/ProfileState.ts'

export interface UserStoreState {
  // Username we are acting as
  viewerRawUsername: null | string,
  userModules: { [key: string]: ProfileState }
}
