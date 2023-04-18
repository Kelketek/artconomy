import mockAxios from '@/specs/helpers/mock-axios'
import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue} from '@vue/test-utils'
import {ArtStore, createStore} from '../../index'
import {rq, rs} from '@/specs/helpers'
import flushPromises from 'flush-promises'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)

jest.useFakeTimers()
const mockClearInterval = jest.spyOn(window, 'clearInterval')
const mockSetInterval = jest.spyOn(window, 'setInterval')

describe('Notifications store', () => {
  let store: ArtStore
  let localVue: VueConstructor
  beforeEach(() => {
    jest.clearAllMocks()
    mockAxios.reset()
    localVue = createLocalVue()
    localVue.use(Vuex)
    store = createStore()
    jest.clearAllTimers()
  })
  it('Sets a loop ID', () => {
    expect((store.state as any).notifications.loopID).toBe(0)
    store.commit('notifications/setLoop', 5)
    expect((store.state as any).notifications.loopID).toBe(5)
  })
  it('Sets notifications stats', () => {
    expect((store.state as any).notifications.stats).toEqual({
      community_count: 0,
      count: 0,
      sales_count: 0,
    })
    store.commit('notifications/setStats', {
      community_count: 3,
      count: 4,
      sales_count: 5,
    })
    expect((store.state as any).notifications.stats).toEqual({
      community_count: 3,
      count: 4,
      sales_count: 5,
    })
  })
  it('Starts a fetching loop', () => {
    expect((store.state as any).notifications.loopID).toBe(0)
    store.dispatch('notifications/startLoop')
    expect((store.state as any).notifications.loopID).toBeGreaterThan(0)
    expect(mockSetInterval).toHaveBeenCalledWith(expect.any(Function), 10000)
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/data/notifications/unread/', 'get', undefined, {}))
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    jest.runOnlyPendingTimers()
    expect(mockAxios.request).toHaveBeenCalledTimes(2)
  })
  it('Does not start a fetching loop if one is already running', async() => {
    await flushPromises()
    // For some reason this is getting polluted, but only for this test. So we want to make sure the number doesn't
    // increase, since that's equivalent to saying it wasn't run.
    const previousCalls = (setInterval as any).mock.calls.length
    store.commit('notifications/setLoop', 87)
    await store.dispatch('notifications/startLoop')
    expect((store.state as any).notifications.loopID).toBe(87)
    expect(setInterval).toHaveBeenCalledTimes(previousCalls)
  })
  it('Clears a fetching loop', () => {
    store.dispatch('notifications/startLoop')
    expect((store.state as any).notifications.loopID).toBeGreaterThan(0)
    const id = (store.state as any).notifications.loopID
    store.dispatch('notifications/stopLoop')
    expect((store.state as any).notifications.loopID).toBe(0)
    expect(mockClearInterval).toHaveBeenCalledWith(id)
  })
  it('Does nothing if told to stop a fetching loop and one is not running', () => {
    expect((store.state as any).notifications.loopID).toBe(0)
    store.dispatch('notifications/stopLoop')
    expect((store.state as any).notifications.loopID).toBe(0)
    expect(mockClearInterval).not.toHaveBeenCalled()
  })
  it('Sets stats after a fetch run', () => {
    store.dispatch('notifications/runFetch')
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/data/notifications/unread/', 'get', undefined, {}))
    mockAxios.mockResponse(rs({
      community_count: 8,
      count: 3,
      sales_count: 2,
    }))
    expect((store.state as any).notifications.stats).toEqual({
      community_count: 8,
      count: 3,
      sales_count: 2,
    })
  })
})
