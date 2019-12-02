import Vue from 'vue'
import Component from 'vue-class-component'

@Component
export default class Nav extends Vue {
  public get fullInterface() {
    const name = this.$route.name || ''
    if (['NewOrder'].indexOf(name) !== -1) {
      return false
    }
    return !name.startsWith('Landing')
  }
}
