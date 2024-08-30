import {FormController} from '@/store/forms/form-controller.ts'
import {RATINGS_SHORT} from '@/lib/lib.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {RatingsValue} from '@/types/Ratings.ts'
import {computed} from 'vue'

export const useContentRatingSearch = (searchForm: FormController) => {
  const {
    rating,
    viewer,
  } = useViewer()
  const ratingItems = computed(() => {
    return Object.keys(RATINGS_SHORT).filter(
      // @ts-ignore
      (val: number) => val <= rating.value).map((key: string) => {
        const value = parseInt(key, 10) as RatingsValue
        return {
          value: parseInt(key, 10),
          title: RATINGS_SHORT[value],
        }
      },
    )
  })
  const contentRatings = computed({
    get: (): RatingsValue[] => {
      return searchForm.fields.content_ratings.value.split(',').sort().filter(
        (val: string) => val !== '',
      ).map((val: string) => parseInt(val, 10))
    },
    set: (val: Array<string | RatingsValue>) => {
      searchForm.fields.content_ratings.update(val.sort().join(','))
    },
  })
  const maxSelected = computed(() => {
    if (!contentRatings.value.length) {
      return 0
    }
    return Math.max(...contentRatings.value) as RatingsValue
  })
  const showRatings = computed(() => {
    return (viewer.value && (!viewer.value.sfw_mode)) && ratingItems.value.length > 1
  })
  return {
    ratingItems,
    contentRatings,
    maxSelected,
    showRatings,
  }
}
