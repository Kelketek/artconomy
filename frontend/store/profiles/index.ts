import Vue from 'vue'
import * as Sentry from '@sentry/browser'
import {ActionTree, GetterTree, Module, MutationTree} from 'vuex'
import {State as RootState} from '../state'
import {UserStoreState} from './types/UserStoreState'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts'
import {ProfileState} from '@/store/profiles/types/ProfileState'

export class ProfileModule {
  public state: ProfileState
  public mutations: MutationTree<ProfileState>
  public actions: ActionTree<ProfileState, UserStoreState>
  public getters: GetterTree<ProfileState, UserStoreState>
  public namespaced = true
  constructor(schema: ProfileModuleOpts) {
    const defaults = {viewer: false, persistent: false}
    this.mutations = {}
    this.actions = {}
    // Actual creation of the relevant singles will happen outside this module.
    this.state = {...defaults, ...schema} as ProfileState
    this.getters = {}
  }
}

// noinspection JSUnusedGlobalSymbols
export const getters: GetterTree<UserStoreState, RootState> = {
}

// noinspection JSUnusedGlobalSymbols
export const actions: ActionTree<UserStoreState, RootState> = {
}

const mutations: MutationTree<UserStoreState> = {
  setViewerUsername(state, username: string) {
    Vue.set(state, 'viewerRawUsername', username)
    /* istanbul ignore next */
    try {
      Sentry.configureScope(scope => {
        scope.setUser({username})
      })
    } catch {
      // Ignore.
    }
  },
}

const profileState = {
  viewerRawUsername: '_',
} as UserStoreState

export const profiles: Module<UserStoreState, RootState> = {
  namespaced: true,
  state: () => ({...profileState}),
  getters,
  actions,
  mutations,
}

export const userModules = {
  namespaced: true,
  state: () => ({}),
  getters: {},
  actions: {},
  mutations: {},
}
