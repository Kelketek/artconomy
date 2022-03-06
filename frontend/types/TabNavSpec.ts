import {RawLocation} from 'vue-router'

export interface TabNavSpec {
  value: RawLocation,
  text: string,
  icon: string,
  count?: number,
}
