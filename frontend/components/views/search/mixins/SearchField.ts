import {RawData} from '@/store/forms/types/RawData.ts'
import deepEqual from 'fast-deep-equal'
import {makeQueryParams} from '@/lib/lib.ts'
import {ListController} from '@/store/lists/controller.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import debounce from 'lodash/debounce'
import {watch} from 'vue'
import {router} from '@/router'


export const useSearchField = (searchForm: FormController, list: ListController<any>) => {
  watch(() => list.params?.page, (newValue?: unknown) => {
    if (newValue === undefined) {
      return
    }
    searchForm.fields.page.update(parseInt(newValue + '', 10))
  })

  watch(() => list.params?.size,(newValue: unknown) => {
    /* istanbul ignore next */
    if (newValue === undefined) {
      return
    }
    searchForm.fields.size.update(newValue)
  })

  const rawUpdate = (newData: RawData) => {
    const newParams = makeQueryParams(newData)
    /* istanbul ignore next */
    const oldParams = makeQueryParams(list.params || {})
    /* istanbul ignore if */
    if (deepEqual(newParams, oldParams)) {
      return
    }
    // I'm not entirely sure how, but this seems to create a situation, sometimes, where we no longer have the list.
    // It might be that I'm reacting to something that destroys this component based on this change.
    list.params = newParams
    /* istanbul ignore next */
    if (!oldParams && (list.ready || list.fetching)) {
      // Already in the process of pulling for the first time. Bail.
      return
    }
    /* istanbul ignore if */
    if (!(list && list.reset)) {
      return
    }
    router.replace({query: newParams}).then(() => {})
    // Same issue here.
    /* istanbul ignore if */
    if (!(list && list.reset)) {
      return
    }
    if (list.ready || list.fetching || list.failed) {
      list.reset().catch(searchForm.setErrors)
    } else {
      list.get()?.catch(searchForm.setErrors)
    }
  }

  watch(() => searchForm.rawData, (newData: RawData) => {
    debouncedUpdate(newData)
  }, {deep: true})

  const debouncedUpdate = debounce(rawUpdate, 250, {trailing: true})

  if (!(list.ready || list.fetching || list.failed)) {
    list.get().then()
  }
  return {
    debouncedUpdate,
    rawUpdate,
  }
}
