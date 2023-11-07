import {Component, mixins} from 'vue-facing-decorator'
import debounce from 'lodash/debounce'
import {FormController} from '@/store/forms/form-controller'
import SearchField from '@/components/views/search/mixins/SearchField'

@Component
export default class SearchList extends mixins(SearchField) {
  public searchForm: FormController = null as unknown as FormController

  public mounted() {
    this.rawUpdate(this.searchForm.rawData)
  }

  public created() {
    this.searchForm = this.$getForm('search')
    this.debouncedUpdate = debounce(this.rawUpdate, 250, {trailing: true})
  }
}
