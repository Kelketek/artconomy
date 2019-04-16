import Component from 'vue-class-component'
import Vue from 'vue'

@Component
export default class Editable extends Vue {
  public unlock() {
    this.$router.replace({query: Object.assign({}, this.$route.query, {editing: true})})
  }
  public lock() {
    const newQuery = {...this.$route.query}
    delete newQuery.editing
    this.$router.replace({query: newQuery})
  }
  public get editing() {
    // Controls must be defined elsewhere.
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
