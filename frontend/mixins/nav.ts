import {Component, Vue} from 'vue-facing-decorator'
import {RouteLocationNormalizedLoaded, useRoute} from 'vue-router'

@Component
export default class Nav extends Vue {
  public get fullInterface() {
    return checkForFullInterface(this.$route)
  }
}

const checkForFullInterface = (route: RouteLocationNormalizedLoaded) => {
  const name = String(route.name || '')
  if (['NewOrder'].indexOf(name) !== -1) {
    return false
  }
  return !name.startsWith('Landing')
}

export const useNav = () => {
  const route = useRoute()
  return checkForFullInterface(route)
}
