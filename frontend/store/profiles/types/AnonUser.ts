import {Ratings} from './Ratings'

export interface AnonUser {
  rating: Ratings,
  blacklist: string[],
  nsfw_blacklist: string[],
  sfw_mode: boolean,
  username: '_',
  birthday: null|string,
}
