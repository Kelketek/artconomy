import {Component, Watch} from 'vue-facing-decorator'
import {Ratings} from '@/store/profiles/types/Ratings.ts'
import {ArtVue, dotTraverse} from '@/lib/lib.ts'
import {ListController} from '@/store/lists/controller.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {watch} from 'vue'

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


export const useRatingRefresh = (lists: ListController<any>[]) => {
  const {rawRating} = useViewer()
  watch(rawRating, () => {
    lists.forEach((list) => list.reset())
  })
}
