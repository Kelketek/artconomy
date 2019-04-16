import Vuex, {Store as VuexStore, StoreOptions} from 'vuex'
import {Alert, AlertCategory, State} from './state'
import {profiles, userModules} from './profiles'
import {errors} from './errors'
import {forms} from './forms'
import {lists} from './lists'
import {cloneDeep} from 'lodash'
import {notifications} from './notifications'
import {genId} from '@/lib'
import {singles} from './singles'
import {characterModules} from '@/store/characters'

export function storeDefaults(): StoreOptions<State> {
  return {
    state: {
      projectName: 'Artconomy',
      showSupport: false,
      markdownHelp: false,
      uploadVisible: false,
      iFrame: false,
      alerts: [],
    },
    mutations: {
      supportDialog(state, value: boolean) {
        state.showSupport = value
      },
      pushAlert(state, alert: Alert) {
        const defaults = {
          category: AlertCategory.SUCCESS,
          timeout: 7000,
          id: genId(),
        }
        const compiled = {...defaults, ...alert}
        state.alerts.push(compiled)
      },
      setMarkdownHelp(state, value: boolean) {
        state.markdownHelp = value
      },
      setUploadVisible(state, value: boolean) {
        state.uploadVisible = value
      },
      popAlert(state) {
        state.alerts.pop()
      },
      setiFrame(state) {
        state.iFrame = true
      },
    },
    getters: {
      latestAlert(state) {
        return state.alerts[state.alerts.length - 1]
      },
      idMap(state) {
        const results: {[key: number]: string} = {}
        const modules = (state as any).userModules
        for (const key of Object.keys(modules)) {
          /* istanbul ignore if */
          if (!modules[key].user) {
            // This property might end up recalculated mid-registration. This is wasteful-- can it be avoided?
            continue
          }
          /* istanbul ignore else */
          if (modules[key].user.x && modules[key].user.x.id) {
            results[modules[key].user.x.id] = modules[key].user.x.username
          }
        }
        return results
      },
    },
    strict: process.env.NODE_ENV !== 'production',
    modules: {
      profiles,
      userModules,
      errors,
      forms,
      notifications,
      lists,
      singles,
      characterModules,
    },
  }
}

export type ArtStore = VuexStore<State>

export const createStore = (options?: StoreOptions<State>): ArtStore => {
  return new Vuex.Store<State>(cloneDeep(options || storeDefaults()))
}
