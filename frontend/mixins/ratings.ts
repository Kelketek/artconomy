import Vue from 'vue'
import Component from 'vue-class-component'
import {RATING_COLOR, RATINGS_SHORT} from '@/lib'

@Component
export default class Ratings extends Vue {
  public ratingsShort = RATINGS_SHORT
  public ratingColor = RATING_COLOR
}
