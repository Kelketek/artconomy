import {RouteLocationNamedRaw} from 'vue-router'

export interface TabNavSpec {
  value: RouteLocationNamedRaw
  title: string,
  icon?: string,
  count?: number,
}
