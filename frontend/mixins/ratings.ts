import {Component} from 'vue-facing-decorator'
import {ArtVue, RATING_COLOR, RATINGS_SHORT} from '@/lib/lib'

@Component
export default class Ratings extends ArtVue {
  public ratingsShort = RATINGS_SHORT
  public ratingColor = RATING_COLOR
}
