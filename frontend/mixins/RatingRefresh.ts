import {Component, Watch} from 'vue-facing-decorator'
import {Ratings} from '@/store/profiles/types/Ratings.ts'
import {ArtVue, dotTraverse} from '@/lib/lib.ts'

@Component
export default class RatingRefresh extends ArtVue {
  public refreshLists: string[] = []
  @Watch('rawRating')
  public refreshListing(newValue: Ratings, oldValue: Ratings|undefined) {
    if (oldValue === undefined) {
      return
    }
    for (const listName of this.refreshLists) {
      dotTraverse(this, listName).reset()
    }
  }
}
