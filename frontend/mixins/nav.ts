import {Component, Vue} from 'vue-facing-decorator'

@Component
export default class Nav extends Vue {
  public get fullInterface() {
    const name = String(this.$route.name || '')
    if (['NewOrder'].indexOf(name) !== -1) {
      return false
    }
    return !name.startsWith('Landing')
  }
}
