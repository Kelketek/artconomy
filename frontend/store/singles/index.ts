import {State as RootState} from '../state'
import {ActionTree, GetterTree, MutationTree} from 'vuex'
import {artCall, ArtCallOptions, immediate} from '@/lib'
import {SingleState} from './types/SingleState'
import _Vue from 'vue'
import {QueryParams} from '@/store/helpers/QueryParams'
import axios from 'axios'

export class SingleModule<T> {
  public state: SingleState<T>
  public mutations: MutationTree<SingleState<T>>
  public actions: ActionTree<SingleState<T>, RootState>
  public getters: GetterTree<SingleState<T>, RootState>
  public namespaced: boolean

  public constructor(options: {
                       x?: T | false | null, endpoint: string, persistent?: boolean,
                       attempted?: boolean, fetching?: boolean, ready?: boolean, failed?: boolean,
                     }
  ) {
    const defaults = {
      x: null, persistent: false, attempted: false, fetching: false, failed: false, ready: false, params: null,
    }
    this.state = {...defaults, ...options}
    const cancel = {source: axios.CancelToken.source()}
    this.mutations = {
      kill(state: SingleState<T>) {
        cancel.source.cancel('Killed.')
        cancel.source = axios.CancelToken.source()
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
        _Vue.set(state, 'x', {...state.x, ...x})
      },
      setX(state: SingleState<T>, x: T | null | false) {
        _Vue.set(state, 'x', x)
      },
      setParams(state: SingleState<T>, params: QueryParams|null) {
        if (params === null) {
          state.params = null
          return
        }
        state.params = {...params}
      },
    }
    this.actions = {
      get({state, commit}) {
        if (state.fetching || state.ready || state.failed) {
          return immediate(state.x)
        }
        commit('kill')
        commit('setFetching', true)
        const getOptions: ArtCallOptions = {url: state.endpoint, method: 'get', cancelToken: cancel.source.token}
        if (state.params) {
          getOptions.params = {...state.params}
        }
        return artCall(getOptions).then((response) => {
          commit('setX', response)
          commit('setReady', true)
          commit('setFailed', false)
          commit('setFetching', false)
          return response
        }).catch((reason) => {
          commit('setReady', false)
          commit('setFetching', false)
          commit('setFailed', true)
          throw reason
        })
      },
      retryGet({state, commit, dispatch}) {
        commit('setFailed', false)
        dispatch('get')
      },
      delete({state, commit}) {
        commit('kill')
        return artCall({
          url: state.endpoint,
          method: 'delete',
          cancelToken: cancel.source.token,
        }).then((response) => {
          commit('setReady', false)
          commit('setX', false)
        })
      },
      put({state, commit}, data: Partial<T> | undefined) {
        commit('kill')
        return artCall({
          url: state.endpoint,
          method: 'put',
          cancelToken: cancel.source.token,
        }).then((response) => {
          commit('setX', response)
        })
      },
      patch({state, commit}, updates: Partial<T>) {
        commit('kill')
        return artCall({
          url: state.endpoint,
          method: 'patch',
          data: updates,
          cancelToken: cancel.source.token,
        }).then((response) => {
          commit('setX', response)
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
