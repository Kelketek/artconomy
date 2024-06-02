import {computed, ref} from 'vue'
import {format} from 'date-fns'

export const useRangeReport = () => {
  const startDate = ref<null|Date>(null)
  const endDate = ref<null|Date>(null)
  const rangeKwargs = computed(() => {
    const kwargs: { [key: string]: string } = {}
    if (startDate.value) {
      kwargs.start_date = format(startDate.value, 'yyyy-MM-dd')
    }
    if (endDate.value) {
      kwargs.end_date = format(endDate.value, 'yyyy-MM-dd')
    }
    return kwargs
  })
  const rangeString = computed(() => {
    const str = Object.keys(rangeKwargs.value).map(key => key + '=' + rangeKwargs.value[key]).join('&')
    if (str) {
      return `?${str}`
    }
    return ''
  })
  return {
    startDate,
    endDate,
    rangeKwargs,
    rangeString,
  }
}
