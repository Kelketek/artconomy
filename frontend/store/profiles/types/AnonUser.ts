import {Ratings} from './Ratings'

export interface AnonUser {
  rating: Ratings,
  blacklist: string[],
  sfw_mode: boolean,
  username: '_'
}
