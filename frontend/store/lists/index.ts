import Vue from 'vue'
import {State as RootState} from '../state'
import {ActionTree, GetterTree, MutationTree, Store} from 'vuex'
import {artCall, ArtCallOptions, immediate} from '@/lib/lib'
import axios from 'axios'
import {ListState} from './types/ListState'
import {PaginatedResponse} from '@/store/lists/types/PaginatedResponse'
import {SingleModule} from '../singles'
import {QueryParams} from '@/store/helpers/QueryParams'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs'

function registerItems(store: Store<any>, state: ListState<any>, items: any[]) {
  if ((state as any).items === undefined) {
    // Build a namespace for the singles.
    store.registerModule([...state.name.split('/'), 'items'], {
      namespaced: true, getters: {}, mutations: {}, actions: {},
    })
  }
  const entries: string[] = []
  for (const item of items) {
    const target = (state as any).items[item[state.keyProp] + '']
    const path = [...state.name.split('/'), 'items', item[state.keyProp] + '']
    if (target !== undefined) {
      store.unregisterModule(path)
    }
    store.registerModule(path, new SingleModule({
      x: item, endpoint: state.endpoint + item[state.keyProp] + '/',
    }))
    entries.push(item[state.keyProp] + '')
  }
  return entries
}

export class ListModule<T extends {}> {
  public state: ListState<T>
  public mutations: MutationTree<ListState<T>>
  public actions: ActionTree<ListState<T>, RootState>
  public getters: GetterTree<ListState<T>, RootState>
  public namespaced: boolean

  public constructor(options: {
                       grow?: boolean, currentPage?: number, endpoint: string, pageSize?: number, persistent?: boolean,
                       keyProp?: keyof T, name: string, reverse?: boolean, failed?: boolean,
                     },
  ) {
    const defaults = {
      grow: false,
      response: null,
      currentPage: 1,
      refs: [],
      pageSize: 24,
      persistent: false,
      ready: false,
      keyProp: 'id' as keyof T,
      fetching: false,
      reverse: false,
      failed: false,
      paginated: true,
      params: null,
    }
    const cancel = {source: axios.CancelToken.source()}
    this.state = {...defaults, ...options}
    this.mutations = {
      setEndpoint(state: ListState<T>, endpoint: string) {
        state.endpoint = endpoint
      },
      kill(state: ListState<T>) {
        // Triggers the cancellation token.
        cancel.source.cancel('Killed.')
        cancel.source = axios.CancelToken.source()
      },
      setResponse(state: ListState<T>, response: PaginatedResponse) {
        if (response === null) {
          state.response = null
          return
        }
        // Other data is sent along. Drop it.
        state.response = {size: response.size, count: response.count}
      },
      push(state, items) {
        const entries = registerItems(this as unknown as Store<any>, state, items)
        state.refs.push(...entries)
      },
      uniquePush(state, items) {
        const entries = registerItems(this as unknown as Store<any>, state, items)
        state.refs.push(...entries.filter((ref: string) => state.refs.indexOf(ref) === -1))
      },
      setReady(state: ListState<T>, value: boolean) {
        state.ready = value
      },
      setGrow(state: ListState<T>, value: boolean) {
        state.grow = value
      },
      setFailed(state: ListState<T>, value: boolean) {
        state.failed = value
      },
      remove(state: ListState<T>, item: T) {
        let index = state.refs.indexOf((item as any)[state.keyProp] + '')
        if (index === -1) {
          return
        }
        while (index !== -1) {
          state.refs.splice(index, 1)
          index = state.refs.indexOf((item as any)[state.keyProp] + '')
        }
        // @ts-ignore
        this.unregisterModule([...state.name.split('/'), 'items', item[state.keyProp] + ''])
      },
      replace(state: ListState<T>, item: T) {
        const index = state.refs.indexOf(item[state.keyProp] + '')
        if (index === -1) {
          console.error(`Attempt to replace non-existent entry based on key '${state.keyProp}':`, item)
          return
        }
        (state as any).items[(item as any)[state.keyProp]].x = item
      },
      setList(state: ListState<T>, items: string[]) {
        const entries = registerItems(this as unknown as Store<any>, state, items)
        Vue.set(state, 'refs', entries)
      },
      setParams(state: ListState<T>, params: QueryParams|null) {
        if (params === null) {
          state.params = null
          return
        }
        state.params = {...params}
      },
      setFetching(state, val: boolean) {
        state.fetching = val
      },
      setPageItems(state, items: T[]) {
        if (state.reverse) {
          items = items.reverse()
        }
        const entries = registerItems(this as unknown as Store<any>, state, items)
        if (state.grow) {
          if (state.reverse) {
            state.refs.unshift(...entries)
          } else {
            state.refs.push(...entries)
          }
          return
        }
        const toRemove = state.refs.filter((x) => entries.indexOf(x) === -1)
        toRemove.map((x: string) => {
          // @ts-ignore
          this.unregisterModule([...state.name.split('/'), 'items', x])
        })
        Vue.set(state, 'refs', entries)
      },
      setCurrentPage(state, val: number) {
        state.currentPage = val
      },
    }
    this.actions = {
      async get({state, commit, dispatch}) {
        /* istanbul ignore next */
        if (state.fetching) {
          cancel.source.cancel()
          cancel.source = axios.CancelToken.source()
        }
        commit('setFetching', true)
        const callOptions: ArtCallOptions = {
          url: state.endpoint,
          method: 'get' as HttpVerbs,
          cancelToken: cancel.source.token,
        }
        let params = state.params || {}
        if (state.paginated) {
          params = {
            ...params,
            ...{
              page: state.currentPage, size: state.pageSize,
            },
          }
        }
        if (Object.keys(params).length) {
          callOptions.params = params
        }
        const response = await artCall(callOptions).catch(
          /* istanbul ignore next */
          (err) => {
            if (!axios.isCancel(err)) {
              commit('setFailed', true)
              commit('setFetching', false)
              throw err
            }
          })
        /* istanbul ignore if */
        if (response === undefined) {
          return
        }
        return dispatch('buildResults', response)
      },
      async firstRun({state, dispatch}) {
        // Runs get if we've never succeeded before and are not fetching.
        // Otherwise does nothing. Useful when Vue reloads components.
        if (state.ready || state.fetching) {
          return immediate(undefined)
        }
        return dispatch('get')
      },
      async buildResults({state, commit, dispatch}, response) {
        if (state.paginated) {
          /* istanbul ignore if */
          if (response.results === undefined) {
            console.error(response, state.endpoint)
            throw Error('No results list. Are you sure this endpoint is paginated?')
          }
          commit('setPageItems', response.results)
          commit('setResponse', response)
        } else {
          commit('setPageItems', response)
          commit('setResponse', null)
        }
        commit('setFetching', false)
        commit('setReady', true)
      },
      async post({state, commit}, item: Partial<T>) {
        commit('kill')
        return artCall({
          url: state.endpoint,
          method: 'post',
          data: item,
          cancelToken: cancel.source.token,
        })
      },
      async reset({commit, dispatch}) {
        commit('kill')
        commit('setReady', false)
        commit('setFetching', false)
        commit('setList', [])
        commit('setResponse', null)
        commit('setCurrentPage', 1)
        return dispatch('firstRun')
      },
      next({state, commit, dispatch, getters}) {
        if (state.currentPage >= getters.totalPages) {
          return
        }
        dispatch('getPage', state.currentPage + 1)
      },
      async retryGet({state, commit, dispatch, getters}) {
        commit('setFailed', false)
        commit('setReady', false)
        return dispatch('get')
      },
      getPage({state, commit, dispatch}, pageNum: number) {
        if (state.currentPage === pageNum) {
          return
        }
        commit('setFailed', false)
        commit('setCurrentPage', pageNum)
        dispatch('get')
      },
    }
    this.getters = {
      totalPages(state) {
        if (!state.response) {
          return 1
        }
        return Math.ceil(state.response.count / state.response.size)
      },
      moreAvailable(state, localGetters) {
        return (!state.fetching) && (localGetters.totalPages > state.currentPage)
      },
    }
    this.namespaced = true
  }
}

export const lists = {
  namespaced: true,
  state: () => ({}),
  actions: {},
  getters: {},
  mutations: {},
}
