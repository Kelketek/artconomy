import { RouteLocationNormalizedLoaded, useRoute } from "vue-router"
import { computed } from "vue"

const checkForFullInterface = (route: RouteLocationNormalizedLoaded) => {
  const name = String(route.name || "")
  if (["NewOrder"].indexOf(name) !== -1) {
    return false
  }
  return !name.startsWith("Landing")
}

export const useNav = () => {
  const route = useRoute()
  return { fullInterface: computed(() => checkForFullInterface(route)) }
}
