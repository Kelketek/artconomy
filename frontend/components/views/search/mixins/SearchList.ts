import Component from 'vue-class-component'
import Vue from 'vue'
import {Watch} from 'vue-property-decorator'
import {makeQueryParams} from '@/lib/lib'
import {debounce, Cancelable} from 'lodash'
import deepEqual from 'fast-deep-equal'
import {ListController} from '@/store/lists/controller'
import {FormController} from '@/store/forms/form-controller'
import {RawData} from '@/store/forms/types/RawData'

@Component
export default class SearchList extends Vue {
  public searchForm: FormController = null as unknown as FormController
  // Must be defined in created function of child.
  public list!: ListController<any>
  public debouncedUpdate!: ((newData: RawData) => void) & Cancelable
  @Watch('searchForm.rawData', {deep: true})
  public updateParams(newData: RawData) {
    this.debouncedUpdate(newData)
  }

  public rawUpdate(newData: RawData) {
    const newParams = makeQueryParams(newData)
    const oldParams = this.list.params
    /* istanbul ignore if */
    if (deepEqual(newParams, oldParams)) {
      return
    }
    // I'm not entirely sure how, but this seems to create a situation, sometimes, where we no longer have the list.
    // It might be that I'm reacting to something that destroys this component based on this change.
    this.list.params = newParams
    /* istanbul ignore if */
    if (!(this.list && this.list.reset)) {
      return
    }
    // My error logs say we sometimes end up with the query string attached to a nonsense place
    this.$router.replace({query: newParams})
    // Same issue here.
    /* istanbul ignore if */
    if (!(this.list && this.list.reset)) {
      return
    }
    this.list.reset().catch(this.searchForm.setErrors)
  }
  public created() {
    this.searchForm = this.$getForm('search')
    this.debouncedUpdate = debounce(this.rawUpdate, 250, {trailing: true})
  }
}
