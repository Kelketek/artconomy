import Component from 'vue-class-component'
import Vue from 'vue'
import {Watch} from 'vue-property-decorator'
import {makeQueryParams} from '@/lib'
import {debounce} from 'lodash'
import deepEqual from 'fast-deep-equal'
import {ListController} from '@/store/lists/controller'
import {FormController} from '@/store/forms/form-controller'
import {RawData} from '@/store/forms/types/RawData'

@Component
export default class SearchList extends Vue {
  public searchForm: FormController = null as unknown as FormController
  // Must be defined in created function of child.
  public list!: ListController<any>
  @Watch('searchForm.rawData', {deep: true})
  public updateParams(newData: RawData) {
    this.debouncedUpdate(newData)
  }

  public get debouncedUpdate() {
    return debounce(this.rawUpdate, 250, {trailing: true})
  }

  public rawUpdate(newData: RawData) {
    const newParams = makeQueryParams(newData)
    const oldParams = this.list.params
    if (deepEqual(newParams, oldParams)) {
      return
    }
    this.list.params = newParams
    this.list.reset().catch(this.searchForm.setErrors)
    this.$router.replace({query: newParams})
  }
  public created() {
    this.searchForm = this.$getForm('search')
  }
}
