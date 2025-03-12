import { ArtState as RootState } from "../artState.ts"
import type {
  ActionTree,
  GetterTree,
  MutationTree,
} from "vuex/types/index.d.ts"
import { artCall, ArtCallOptions, immediate } from "@/lib/lib.ts"
import { QueryParams } from "@/store/helpers/QueryParams.ts"

import type {
  SingleSocketSettings,
  SingleState,
} from "@/store/singles/types.d.ts"

export class SingleModule<T> {
  public state: SingleState<T>
  public mutations: MutationTree<SingleState<T>>
  public actions: ActionTree<SingleState<T>, RootState>
  public getters: GetterTree<SingleState<T>, RootState>
  public namespaced: boolean

  public constructor(options: {
    x?: T | null
    endpoint: string
    persistent?: boolean
    attempted?: boolean
    fetching?: boolean
    ready?: boolean
    failed?: boolean
    deleted?: boolean
    socketSettings?: SingleSocketSettings | null
  }) {
    const defaults = {
      x: null,
      persistent: false,
      attempted: false,
      fetching: false,
      failed: false,
      ready: false,
      params: null,
      deleted: false,
      socketSettings: null,
    }
    this.state = { ...defaults, ...options }
    const cancel = { source: new AbortController() }
    this.mutations = {
      kill() {
        cancel.source.abort()
        cancel.source = new AbortController()
      },
      setEndpoint(state: SingleState<T>, endpoint: string) {
        state.endpoint = endpoint
      },
      setReady(state: SingleState<T>, val: boolean) {
        state.ready = val
      },
      setFailed(state: SingleState<T>, val: boolean) {
        state.failed = val
      },
      setFetching(state: SingleState<T>, val: boolean) {
        state.fetching = val
      },
      updateX(state: SingleState<T>, x: Partial<T>) {
        state.x = { ...(state.x as T), ...x }
      },
      setX(state: SingleState<T>, x: T | null) {
        state.x = x
      },
      setSocketSettings(
        state: SingleState<T>,
        val: SingleSocketSettings | null,
      ) {
        state.socketSettings = val
      },
      setDeleted(state: SingleState<T>, val: boolean) {
        state.deleted = val
      },
      setParams(state: SingleState<T>, params: QueryParams | null) {
        if (params === null) {
          state.params = null
          return
        }
        state.params = { ...params }
      },
    }
    this.actions = {
      get({ state, commit }) {
        if (state.fetching || state.ready || state.failed) {
          return immediate(state.x)
        }
        commit("kill")
        commit("setFetching", true)
        const getOptions: ArtCallOptions = {
          url: state.endpoint,
          method: "get",
          signal: cancel.source.signal,
        }
        if (state.params) {
          getOptions.params = { ...state.params }
        }
        return artCall(getOptions)
          .then((response) => {
            commit("setX", response)
            commit("setReady", true)
            commit("setFailed", false)
            commit("setFetching", false)
            return response
          })
          .catch((reason) => {
            // Can't test this because the mock-axios library does not implement cancel tokens.
            /* istanbul ignore if */
            if (reason && reason.message === "Killed.") {
              return
            }
            commit("setReady", false)
            commit("setFetching", false)
            commit("setFailed", true)
            throw reason
          })
      },
      retryGet({ commit, dispatch }) {
        commit("setFailed", false)
        dispatch("get")
      },
      delete({ state, commit }) {
        commit("kill")
        return artCall({
          url: state.endpoint,
          method: "delete",
          signal: cancel.source.signal,
        }).then(() => {
          commit("setDeleted", true)
          commit("setReady", false)
          commit("setX", null)
        })
      },
      put({ state, commit }, data: Partial<T> | undefined) {
        commit("kill")
        return artCall({
          url: state.endpoint,
          method: "put",
          signal: cancel.source.signal,
          data,
        }).then((response) => {
          commit("setX", response)
        })
      },
      patch({ state, commit }, updates: Partial<T>) {
        commit("kill")
        return artCall({
          url: state.endpoint,
          method: "patch",
          data: updates,
          signal: cancel.source.signal,
        }).then((response) => {
          commit("setX", response)
        })
      },
      post({ state, commit }, data: any) {
        commit("kill")
        return artCall({
          url: state.endpoint,
          method: "post",
          data,
          signal: cancel.source.signal,
        })
      },
    }
    this.getters = {}
    this.namespaced = true
  }
}

export const singles = {
  namespaced: true,
  state: () => ({}),
  actions: {},
  getters: {},
  mutations: {},
}
