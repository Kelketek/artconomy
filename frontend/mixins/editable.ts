import {Component} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib.ts'
import {RouteLocation, Router, useRoute, useRouter} from 'vue-router'
import {computed, ComputedRef} from 'vue'

@Component
export default class Editable extends ArtVue {
  // Controls must be defined on the child class.
  // Unfortunately the decorator class somehow manages to turn this into undefined
  // Even if just annotating like below.
  // public controls!: boolean;

  public async unlock() {
    return unlockRoute(this.$router, this.$route)
  }

  public lock() {
    return lockRoute(this.$router, this.$route)
  }

  public get editing() {
    // @ts-ignore
    return Boolean(this.controls && this.$route.query.editing)
  }

  public set editing(value) {
    if (value) {
      this.unlock().then()
    } else {
      this.lock().then()
    }
  }
}

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
        lock().then()
      } else {
        unlock().then()
      }
    }
  })

  return {
    lock,
    unlock,
    editing,
  }
}
