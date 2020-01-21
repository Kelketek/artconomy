import {State as RootState} from '../state'
import {ActionTree, GetterTree, MutationTree} from 'vuex'
import {artCall} from '@/lib/lib'
import {NotificationsState} from '@/store/notifications/types/NotificationsState'
import {NotificationStats} from '@/store/notifications/types/NotificationStats'

const getters: GetterTree<NotificationsState, RootState> = {}

const mutations: MutationTree<NotificationsState> = {
  setStats(state: NotificationsState, stats: NotificationStats) {
    state.stats = stats
  },
  setLoop(state: NotificationsState, loopID: number) {
    state.loopID = loopID
  },
}

// noinspection JSUnusedGlobalSymbols
const actions: ActionTree<NotificationsState, RootState> = {
  startLoop({state, dispatch, commit}) {
    if (state.loopID) {
      return
    }
    commit('setLoop', (setInterval(() => {
      dispatch('runFetch')
    }, 10000)))
    // Run the first time immediately.
    dispatch('runFetch')
  },
  stopLoop({commit, state}) {
    if (!state.loopID) {
      return
    }
    clearInterval(state.loopID)
    commit('setLoop', 0)
  },
  runFetch({commit}) {
    artCall({url: '/api/profiles/v1/data/notifications/unread/', method: 'get'}
    ).then((response: NotificationStats) => {
      commit('setStats', response)
    }).catch(() => {})
  },
}

const notificationsState: NotificationsState = {
  stats: {
    count: 0,
    community_count: 0,
    sales_count: 0,
  },
  loopID: 0,
}

export const notifications = {
  namespaced: true,
  state: notificationsState,
  getters,
  mutations,
  actions,
}
