import {createStore as createVuexStore, Store as VuexStore, StoreOptions} from 'vuex'
import {Alert, AlertCategory, ArtState} from './artState.ts'
import {profiles, userModules} from './profiles/index.ts'
import {errors} from './errors/index.ts'
import {forms} from './forms/index.ts'
import {lists} from './lists/index.ts'
import cloneDeep from 'lodash/cloneDeep'
import {genId} from '@/lib/lib.ts'
import {singles} from './singles/index.ts'
import {characterModules} from '@/store/characters/index.ts'
import {RatingsValue} from '@/types/Ratings.ts'

export function storeDefaults(): StoreOptions<ArtState> {
  return {
    state: {
      projectName: 'Artconomy',
      showSupport: false,
      markdownHelp: false,
      uploadVisible: false,
      iFrame: false,
      searchInitialized: false,
      alerts: [],
      ageAsked: false,
      contentRating: 0,
      messagesOpen: false,
      showAgeVerification: false,
      showCookieDialog: false,
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
      setSearchInitialized(state, value: boolean) {
        state.searchInitialized = value
      },
      setAgeAsked(state, value: boolean) {
        state.ageAsked = value
      },
      setContentRating(state, value: RatingsValue) {
        state.contentRating = value
      },
      setShowAgeVerification(state, value: boolean) {
        state.showAgeVerification = value
      },
      setShowCookieDialog(state, value: boolean) {
        state.showCookieDialog = value
      },
      setMessagesOpen(state, value: boolean) {
        state.messagesOpen = value
      }
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
    // You might enable this in development to look for bugs, but most of our commits are automatically constructed,
    // and enabling it will set up deep watchers that kill performance to a frustrating degree.
    strict: false,
    modules: {
      profiles,
      userModules,
      errors,
      forms,
      lists,
      singles,
      characterModules,
    },
  }
}

export type ArtStore = VuexStore<ArtState>


export const createStore = (options?: StoreOptions<ArtState>): ArtStore => {
  return createVuexStore<ArtState>({...cloneDeep(options || storeDefaults()), plugins: [/**myPlugin**/]})
}
