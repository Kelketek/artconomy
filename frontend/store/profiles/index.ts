import * as Sentry from '@sentry/browser'
import {ActionTree, GetterTree, Module, MutationTree} from 'vuex'
import {ArtState as RootState} from '../artState.ts'
import {ProfileModuleOpts, ProfileState, UserStoreState} from '@/store/profiles/types/main'

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
    state.viewerRawUsername = username
    /* istanbul ignore next */
    try {
      const scope = Sentry.getCurrentScope()
      scope.setUser({username})
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
