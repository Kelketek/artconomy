import Component from 'vue-class-component'
import Vue from 'vue'

@Component
export default class Editable extends Vue {
  // Controls must be defined elsewhere.
  public controls!: boolean;
  public unlock() {
    this.$router.replace({query: Object.assign({}, this.$route.query, {editing: true})})
  }

  public lock() {
    const newQuery = {...this.$route.query}
    delete newQuery.editing
    this.$router.replace({query: newQuery})
  }

  public get editing() {
    const value = Boolean(this.controls && this.$route.query.editing)
    return value
  }

  public set editing(value) {
    if (value) {
      this.unlock()
    } else {
      this.lock()
    }
  }
}
