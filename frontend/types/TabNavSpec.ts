import {Location} from 'vue-router'

export interface TabNavSpec {
  value: Location,
  text: string,
  icon: string,
  count?: number,
}
