import {Ratings} from './Ratings.ts'

export interface AnonUser {
  rating: Ratings,
  blacklist: string[],
  nsfw_blacklist: string[],
  sfw_mode: boolean,
  username: '_',
  birthday: null|string,
  artist_mode?: undefined,
  avatar_url?: undefined
  is_staff?: undefined,
  is_superuser?: undefined,
}
