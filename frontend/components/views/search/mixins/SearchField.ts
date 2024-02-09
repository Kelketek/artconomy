import {RawData} from '@/store/forms/types/RawData.ts'
import deepEqual from 'fast-deep-equal'
import {makeQueryParams} from '@/lib/lib.ts'
import {ListController} from '@/store/lists/controller.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import debounce from 'lodash/debounce'
import {Component, mixins, Watch} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'

@Component
export default class SearchField extends mixins(Viewer) {
  // list and searchForm must be defined on subclass.
  public list!: ListController<any>
  public searchForm!: FormController
  public debouncedUpdate!: ((newData: RawData) => void)
  public updateRouter = true

  @Watch('list.params.page')
  public updatePage(newValue: number | undefined) {
    /* istanbul ignore next */
    if (newValue === undefined || this.searchForm === null) {
      return
    }
    this.searchForm.fields.page.update(newValue)
  }

  @Watch('list.params.size')
  public updateSize(newValue: number | undefined) {
    /* istanbul ignore next */
    if (newValue === undefined || this.searchForm === null) {
      return
    }
    this.searchForm.fields.size.update(newValue)
  }

  @Watch('searchForm.rawData', {deep: true})
  public updateParams(newData: RawData) {
    if (!this.$store.state.searchInitialized) {
      return
    }
    this.debouncedUpdate(newData)
  }

  public rawUpdate(newData: RawData) {
    const newParams = makeQueryParams(newData)
    /* istanbul ignore next */
    const oldParams = makeQueryParams(this.list.params || {})
    /* istanbul ignore if */
    if (deepEqual(newParams, oldParams)) {
      return
    }
    // I'm not entirely sure how, but this seems to create a situation, sometimes, where we no longer have the list.
    // It might be that I'm reacting to something that destroys this component based on this change.
    this.list.params = newParams
    /* istanbul ignore next */
    if (!oldParams && (this.list.ready || this.list.fetching)) {
      // Already in the process of pulling for the first time. Bail.
      return
    }
    /* istanbul ignore if */
    if (!(this.list && this.list.reset)) {
      return
    }
    /* istanbul ignore else */
    if (this.updateRouter) {
      // My error logs say we sometimes end up with the query string attached to a nonsense place. If this is undefined,
      // it should bail.
      this.$router.replace({query: newParams})
    }
    // Same issue here.
    /* istanbul ignore if */
    if (!(this.list && this.list.reset)) {
      return
    }
    if (this.list.ready || this.list.fetching || this.list.failed) {
      this.list.reset().catch(this.searchForm.setErrors)
    } else {
      this.list.get().catch(this.searchForm.setErrors)
    }
  }

  public created() {
    this.debouncedUpdate = debounce(this.rawUpdate, 250, {trailing: true})
    this.$nextTick(() => {
      if (!(this.list.ready || this.list.fetching || this.list.failed)) {
        this.list.get().then()
      }
    })
  }
}
