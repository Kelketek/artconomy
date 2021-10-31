import Vue from 'vue'
import Component from 'vue-class-component'
import {Watch} from 'vue-property-decorator'
import {Ratings} from '@/store/profiles/types/Ratings'
import {dotTraverse} from '@/lib/lib'

@Component
export default class RatingRefresh extends Vue {
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
