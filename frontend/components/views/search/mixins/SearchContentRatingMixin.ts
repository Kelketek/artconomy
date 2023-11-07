import {Component, mixins} from 'vue-facing-decorator'
import {FormController} from '@/store/forms/form-controller'
import {RATING_COLOR, RATINGS_SHORT} from '@/lib/lib'
import Viewer from '@/mixins/viewer'
import {ContentRating} from '@/types/ContentRating'

@Component
export default class SearchContentRatingMixin extends mixins(Viewer) {
  // Must be defined in created function of child.
  public searchForm: FormController = null as unknown as FormController
  public ratingsShort = RATINGS_SHORT
  public ratingColor = RATING_COLOR

  public get ratingItems() {
    return Object.keys(RATINGS_SHORT).filter(
      // @ts-ignore
      (val: number) => val <= this.rating).map((key: ContentRating) => ({
        value: key,
        title: RATINGS_SHORT[key],
      }),
    )
  }

  public get maxSelected() {
    if (!this.contentRatings.length) {
      return 0
    }
    return Math.max(...this.contentRatings)
  }

  public get showRatings() {
    return (this.viewer && (!this.viewer!.sfw_mode)) && this.ratingItems.length > 1
  }

  public get contentRatings(): ContentRating[] {
    if (!this.searchForm) {
      return []
    }
    return this.searchForm.fields.content_ratings.value.split(',').sort().filter(
      (val: string) => val !== '',
    ).map((val: string) => parseInt(val, 10))
  }

  public set contentRatings(val: string[]) {
    this.searchForm.fields.content_ratings.update(val.sort().join(','))
  }
}
