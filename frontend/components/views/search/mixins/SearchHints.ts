import Vue from 'vue'
import Component from 'vue-class-component'
import {FormController} from '@/store/forms/form-controller'

@Component
export default class SearchHints extends Vue {
  public searchForm: FormController = null as unknown as FormController

  public search(val: string) {
    this.searchForm.fields.q.update(val)
  }

  public created() {
    this.searchForm = this.$getForm('search')
  }
}
