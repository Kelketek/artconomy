import {ErrorState} from './types.ts'
import {AxiosError} from 'axios'
import {MutationTree} from 'vuex'

const mutations: MutationTree<ErrorState> = {
  clearError(state: ErrorState) {
    state.code = 0
  },
  setError(state: ErrorState, error: AxiosError | { response: { status: number } }) {
    // Can't test this since mock-axios doesn't implement cancellation.
    /* istanbul ignore if */
    // @ts-expect-error Checking potentially undefined prop.
    if (error && error.message === 'Killed.') {
      return
    }
    state.code = (error.response || {status: 503}).status
  },
}

export const errors = {
  namespaced: true,
  state: () => ({code: 0}),
  mutations,
}
