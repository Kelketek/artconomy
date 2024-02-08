import {State as RootState} from '../state.ts'
import {ActionTree, MutationTree, Store} from 'vuex'
import {artCall, ArtCallOptions, immediate} from '@/lib/lib.ts'
import axios from 'axios'
import {ListState} from './types/ListState.ts'
import {PaginatedResponse} from '@/store/lists/types/PaginatedResponse.ts'
import {SingleModule} from '../singles/index.ts'
import {QueryParams} from '@/store/helpers/QueryParams.ts'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs.ts'
import {ListSocketSettings} from '@/store/lists/types/ListSocketSettings.ts'
import {SingleSocketSettings} from '@/store/singles/types/SingleSocketSettings.ts'

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
    let socketSettings: SingleSocketSettings|null
    if (state.socketSettings !== null) {
      socketSettings = {...state.socketSettings}
    } else {
      socketSettings = null
    }
    store.registerModule(path, new SingleModule({
      x: item,
      endpoint: state.endpoint + item[state.keyProp] + '/',
      ready: true,
      socketSettings: socketSettings,
    }))
    entries.push(item[state.keyProp] + '')
  }
  return entries
}

export const pageFromParams = (params: QueryParams) => {
  /* istanbul ignore next */
  return parseInt(`${(params && params.page) || 1}`, 10)
}

export const totalPages = (response: PaginatedResponse | undefined | null) => {
  if (!response) {
    return 1
  }
  return Math.ceil(response.count / response.size)
}

export const pageSizeFromParams = (params: QueryParams) => {
  /* istanbul ignore next */
  const rawData = {size: 24, ...params}
  return parseInt(`${(params && params.size) || 24}`, 10)
}

const defaultParams = (state: ListState<any>, params: QueryParams) => {
  let newParams = params
  if (state.paginated) {
    newParams = newParams || {}
    if (!newParams.page) {
      newParams.page = 1
    }
    if (!newParams.size) {
      newParams.size = 24
    }
  }
  return newParams
}

export class ListModule<T extends {}> {
  public state: ListState<T>
  public mutations: MutationTree<ListState<T>>
  public actions: ActionTree<ListState<T>, RootState>
  public namespaced: boolean

  public constructor(options: {
                       grow?: boolean, currentPage?: number, endpoint: string, persistent?: boolean,
                       keyProp?: keyof T, name: string, reverse?: boolean, failed?: boolean, stale?: boolean,
                       socketSettings?: ListSocketSettings, params?: QueryParams,
                     },
  ) {
    const defaults = {
      grow: false,
      response: null,
      refs: [],
      persistent: false,
      ready: false,
      keyProp: 'id' as keyof T,
      fetching: false,
      reverse: false,
      failed: false,
      paginated: true,
      params: {},
      socketSettings: null,
      stale: false,
    }
    const cancel = {source: new AbortController()}
    this.state = {...defaults, ...options}
    this.state.params = defaultParams(this.state, this.state.params)
    this.mutations = {
      setEndpoint(state: ListState<T>, endpoint: string) {
        state.endpoint = endpoint
      },
      kill(state: ListState<T>) {
        // Triggers the cancellation token.
        cancel.source.abort('Killed.')
        cancel.source = new AbortController()
      },
      setResponse(state: ListState<T>, response: PaginatedResponse) {
        if (response === null) {
          state.response = null
          return
        }
        // Other data is sent along. Drop it.
        state.response = {size: response.size, count: response.count}
      },
      unshift(state, items) {
        const entries = registerItems(this as unknown as Store<any>, state, items)
        state.refs.unshift(...entries)
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
      setStale(state: ListState<T>, value: boolean) {
        state.stale = value
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
          return
        }
        (state as any).items[(item as any)[state.keyProp]].x = item
      },
      setList(state: ListState<T>, items: string[]) {
        state.refs = registerItems(this as unknown as Store<any>, state, items)
      },
      setSocketSettings(state: ListState<T>, socketSettings: ListSocketSettings) {
        state.socketSettings = socketSettings
      },
      setParams(state: ListState<T>, params: QueryParams) {
        state.params = defaultParams(state, params)
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
        toRemove.map((x: string) => { // eslint-disable-line array-callback-return
          // @ts-ignore
          this.unregisterModule([...state.name.split('/'), 'items', x])
        })
        state.refs = entries
      },
      setCurrentPage(state, val: number) {
        /* istanbul ignore next */
        const params = state.params || {}
        params.page = val
        state.params = params
      },
    }
    this.actions = {
      async get({state, commit, dispatch}) {
        /* istanbul ignore next */
        if (state.fetching) {
          cancel.source.abort()
          cancel.source = new AbortController()
        }
        commit('setFetching', true)
        const callOptions: ArtCallOptions = {
          url: state.endpoint,
          method: 'get' as HttpVerbs,
          signal: cancel.source.signal,
        }
        const params = state.params || {}
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
          signal: cancel.source.signal,
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
      async next({state, commit, dispatch, getters}) {
        if (state.params && pageFromParams(state.params) >= totalPages(state.response)) {
          return
        }
        return dispatch('getPage', pageFromParams(state.params) + 1)
      },
      async retryGet({state, commit, dispatch, getters}) {
        commit('setFailed', false)
        commit('setReady', false)
        return dispatch('get')
      },
      async getPage({state, commit, dispatch}, pageNum: number) {
        if (pageFromParams(state.params) === pageNum) {
          return
        }
        commit('setFailed', false)
        commit('setCurrentPage', pageNum)
        return dispatch('get')
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
