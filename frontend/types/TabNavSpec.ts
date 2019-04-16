import {Route} from 'vue-router'

export interface TabNavSpec {
  value: Route,
  text: string,
  icon: string,
  count?: number,
}
