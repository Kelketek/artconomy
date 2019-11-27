import {State as RootState} from '../state'
import {ErrorState} from './types'
import {AxiosError} from 'axios'
import {GetterTree, MutationTree} from 'vuex'

const getters: GetterTree<ErrorState, RootState> = {
  logo(state): string {
    if ([500, 503, 400, 404, 403].indexOf(state.code) !== -1) {
      return `/static/images/${state.code}.png`
    } else {
      return `/static/images/generic-error.png`
    }
  },
}

const mutations: MutationTree<ErrorState> = {
  clearError(state: ErrorState) {
    state.code = 0
  },
  setError(state: ErrorState, error: AxiosError | { response: { status: number } }) {
    // Maybe find a different non-connection error code for this later.
    state.code = (error.response || {status: 503}).status
  },
}

export const errors = {
  namespaced: true,
  state: () => ({code: 0}),
  getters,
  mutations,
}
