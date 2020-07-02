import Component, {mixins} from 'vue-class-component'
import {debounce, Cancelable} from 'lodash'
import {ListController} from '@/store/lists/controller'
import {FormController} from '@/store/forms/form-controller'
import {RawData} from '@/store/forms/types/RawData'
import SearchField from '@/components/views/search/mixins/SearchField'

@Component
export default class SearchList extends mixins(SearchField) {
  public searchForm: FormController = null as unknown as FormController
  // Must be defined in created function of child.
  public list!: ListController<any>
  public debouncedUpdate!: ((newData: RawData) => void) & Cancelable
  public created() {
    this.searchForm = this.$getForm('search')
    this.debouncedUpdate = debounce(this.rawUpdate, 250, {trailing: true})
  }
}
