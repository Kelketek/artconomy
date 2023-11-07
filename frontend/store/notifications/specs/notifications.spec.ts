import mockAxios from '@/specs/helpers/mock-axios'
import {ArtStore, createStore} from '../../index'
import {rq, rs} from '@/specs/helpers'
import flushPromises from 'flush-promises'
import {beforeEach, describe, expect, test, vi} from 'vitest'

vi.useFakeTimers()
const mockClearInterval = vi.spyOn(window, 'clearInterval')
const mockSetInterval = vi.spyOn(window, 'setInterval')

describe('Notifications store', () => {
  let store: ArtStore
  beforeEach(() => {
    vi.clearAllMocks()
    mockAxios.reset()
    store = createStore()
    vi.clearAllTimers()
  })
  test('Sets a loop ID', () => {
    expect((store.state as any).notifications.loopID).toBe(0)
    store.commit('notifications/setLoop', 5)
    expect((store.state as any).notifications.loopID).toBe(5)
  })
  test('Sets notifications stats', () => {
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
  test('Starts a fetching loop', () => {
    expect((store.state as any).notifications.loopID).toBe(0)
    store.dispatch('notifications/startLoop')
    expect((store.state as any).notifications.loopID).toBeTruthy
    expect(mockSetInterval).toHaveBeenCalledWith(expect.any(Function), 10000)
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/data/notifications/unread/', 'get', undefined, {}))
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    vi.runOnlyPendingTimers()
    expect(mockAxios.request).toHaveBeenCalledTimes(2)
  })
  test('Does not start a fetching loop if one is already running', async() => {
    await flushPromises()
    // For some reason this is getting polluted, but only for this test. So we want to make sure the number doesn't
    // increase, since that's equivalent to saying it wasn't run.
    const previousCalls = (setInterval as any).mock.calls.length
    store.commit('notifications/setLoop', 87)
    await store.dispatch('notifications/startLoop')
    expect((store.state as any).notifications.loopID).toBe(87)
    expect(setInterval).toHaveBeenCalledTimes(previousCalls)
  })
  test('Clears a fetching loop', () => {
    store.dispatch('notifications/startLoop')
    expect((store.state as any).notifications.loopID).toBeTruthy
    const id = (store.state as any).notifications.loopID
    store.dispatch('notifications/stopLoop')
    expect((store.state as any).notifications.loopID).toBe(0)
    expect(mockClearInterval).toHaveBeenCalledWith(id)
  })
  test('Does nothing if told to stop a fetching loop and one is not running', () => {
    expect((store.state as any).notifications.loopID).toBe(0)
    store.dispatch('notifications/stopLoop')
    expect((store.state as any).notifications.loopID).toBe(0)
    expect(mockClearInterval).not.toHaveBeenCalled()
  })
  test('Sets stats after a fetch run', () => {
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
