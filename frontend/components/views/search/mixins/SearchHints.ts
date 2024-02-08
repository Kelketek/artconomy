import {Component} from 'vue-facing-decorator'
import {FormController} from '@/store/forms/form-controller.ts'
import {ArtVue} from '@/lib/lib.ts'

@Component
export default class SearchHints extends ArtVue {
  public searchForm: FormController = null as unknown as FormController

  public search(val: string) {
    this.searchForm.fields.q.update(val)
  }

  public created() {
    this.searchForm = this.$getForm('search')
  }
}
