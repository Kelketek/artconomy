import {Component} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib.ts'

@Component
export default class Editable extends ArtVue {
  // Controls must be defined on the child class.
  // Unfortunately the decorator class somehow manages to turn this into undefined
  // Even if just annotating like below.
  // public controls!: boolean;

  public unlock() {
    this.$router.replace({query: Object.assign({}, this.$route.query, {editing: true})})
  }

  public lock() {
    const newQuery = {...this.$route.query}
    delete newQuery.editing
    this.$router.replace({query: newQuery})
  }

  public get editing() {
    // @ts-ignore
    return Boolean(this.controls && this.$route.query.editing)
  }

  public set editing(value) {
    if (value) {
      this.unlock()
    } else {
      this.lock()
    }
  }
}
