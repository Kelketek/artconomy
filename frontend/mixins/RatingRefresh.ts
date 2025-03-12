import { ListController } from "@/store/lists/controller.ts"
import { useViewer } from "@/mixins/viewer.ts"
import { watch } from "vue"

export const useRatingRefresh = (lists: ListController<any>[]) => {
  const { rawRating } = useViewer()
  watch(rawRating, () => {
    lists.forEach((list) => list.reset())
  })
}
