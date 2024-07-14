import {RouteLocation, Router, useRoute, useRouter} from 'vue-router'
import {computed, ComputedRef} from 'vue'

const unlockRoute = async (router: Router, route: RouteLocation) => {
  return router.replace({query: {...route.query, editing: 'true'}})
}

const lockRoute = async (router: Router, route: RouteLocation) => {
  const newQuery = {...route.query}
  delete newQuery.editing
  return router.replace({query: newQuery})
}

export const useEditable = (controls: ComputedRef<boolean>) => {
  const router = useRouter()
  const route = useRoute()
  const lock = () => lockRoute(router, route)
  const unlock = () => unlockRoute(router, route)

  const editing = computed({
    get: () => {
      return Boolean(controls.value && route.query.editing)
    },
    set: (val: boolean) => {
      if (val) {
        unlock().then()
      } else {
        lock().then()
      }
    }
  })

  return {
    lock,
    unlock,
    editing,
  }
}
