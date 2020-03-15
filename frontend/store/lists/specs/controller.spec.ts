import {ListController} from '../controller'
import {listRegistry} from '../registry'
import {ArtStore, createStore} from '../../index'
import {createLocalVue, shallowMount} from '@vue/test-utils'
import mockAxios from '@/specs/helpers/mock-axios'
import Vue from 'vue'
import Vuex from 'vuex'
import {rq, rs} from '@/specs/helpers'
import flushPromises from 'flush-promises'
import {ListModuleOpts} from '../types/ListModuleOpts'
import {singleRegistry, Singles} from '../../singles/registry'

let store: ArtStore
let state: any
Vue.use(Vuex)
const localVue = createLocalVue()
localVue.use(Singles)

const mockError = jest.spyOn(console, 'error')

describe('List controller', () => {
  function makeController(extra?: Partial<ListModuleOpts>) {
    if (extra === undefined) {
      extra = {}
    }
    return shallowMount(ListController, {
      store,
      propsData: {
        initName: 'example',
        schema: {...{endpoint: '/endpoint/'}, ...extra},
      },
      localVue,
    }
    ).vm as ListController<any>
  }

  beforeEach(() => {
    listRegistry.reset()
    singleRegistry.reset()
    store = createStore()
    state = (store.state as any).lists
    mockAxios.reset()
  })
  it('Initializes a list', () => {
    const controller = makeController()
    expect(state.example).toBeTruthy()
    expect(state.example.endpoint).toBe('/endpoint/')
  })
  it('Picks up an existing list', () => {
    const controller = makeController()
    const newController = new ListController({
      store, propsData: {initName: 'example', schema: {endpoint: '/test/'}},
    })
    expect(controller.endpoint).toBe(newController.endpoint)
    expect(controller.endpoint).toBe('/endpoint/')
  })
  it('Returns the endpoint', () => {
    const controller = makeController()
    expect(controller.endpoint).toBe('/endpoint/')
  })
  it('Sets the endpoint', () => {
    const controller = makeController()
    controller.endpoint = '/test/'
    expect(state.example.endpoint).toBe('/test/')
  })
  it('Retrieves the page size', () => {
    const controller = makeController({pageSize: 5})
    expect(controller.pageSize).toBe(5)
  })
  it('Proclaims the total pagecount as 1 when response is null', () => {
    const controller = makeController()
    expect(controller.totalPages).toBe(1)
  })
  it('Calculates the correct number of total pages', () => {
    const controller = makeController()
    store.commit('lists/example/setResponse', {
      results: [],
      count: 50,
      size: 24,
    })
    expect(controller.totalPages).toBe(3)
  })
  it('Gets the ready status', () => {
    const controller = makeController()
    expect(controller.ready).toBe(false)
  })
  it('Gets the list', async() => {
    const controller = makeController()
    await store.commit('lists/example/setList', [{id: 1, test: 'thing', test2: 'thingy'}])
    expect(controller.list.map((x: any) => x.x)).toEqual([{id: 1, test: 'thing', test2: 'thingy'}])
  })
  it('Sets the list', () => {
    const controller = makeController()
    controller.setList([{id: 1}, {id: 2}, {id: 3}, {id: 4}])
    expect(state.example.refs).toEqual(['1', '2', '3', '4'])
    expect(state.example.items['1'].x.id).toBe(1)
    expect(state.example.items['2'].x.id).toBe(2)
    expect(state.example.items['3'].x.id).toBe(3)
    expect(state.example.items['4'].x.id).toBe(4)
  })
  it('Resets the list', () => {
    const controller = makeController()
    controller.response = {
      count: 2,
      size: 24,
    }
    controller.ready = true
    controller.setList([{id: 1}, {id: 2}, {id: 3}, {id: 4}])
    controller.commit('setCurrentPage', 3)
    controller.reset()
    expect(controller.ready).toBe(false)
    expect(controller.list).toEqual([])
    expect(controller.currentPage).toBe(1)
    expect(controller.fetching).toBe(true)
  })
  it('Grabs and sets the params', () => {
    const controller = makeController({params: {stuff: 'things', wat: 'do'}})
    expect(controller.params).toEqual({stuff: 'things', wat: 'do'})
    controller.params = {dude: 'sweet'}
    expect(controller.params).toEqual({dude: 'sweet'})
    controller.params = null
    expect(controller.params).toBe(null)
  })
  it('Removes an item from the list', async() => {
    const controller = makeController()
    const item1 = {id: 1}
    const item2 = {id: 2}
    const item3 = {id: 3}
    await store.commit('lists/example/setList', [item1, item2, item3])
    controller.remove(item2)
    expect(state.example.refs).toEqual(['1', '3'])
  })
  it('Replaces an item in the list', () => {
    const controller = makeController()
    const item1 = {id: 1, test: 'Hello'}
    const item2 = {id: 2, test: 'Goodbye'}
    const item3 = {id: 3, test: 'Aloha'}
    store.commit('lists/example/setList', [item1, item2, item3])
    const replacement = {id: 2, test: 'Surprise, Mothafucka'}
    controller.replace(replacement)
    expect(state.example.refs).toEqual(['1', '2', '3'])
    expect(state.example.items['2'].x).toEqual(replacement)
  })
  it('Pushes an onto the end of the list', () => {
    const controller = makeController()
    const item1 = {id: 1, test: 'Hello'}
    const item2 = {id: 2, test: 'Goodbye'}
    const item3 = {id: 3, test: 'Aloha'}
    store.commit('lists/example/setList', [item1, item2, item3])
    const item4 = {id: 4, test: 'Surprise, Mothafucka'}
    controller.push(item4)
    expect(state.example.refs).toEqual(['1', '2', '3', '4'])
  })
  it('Does nothing if attempting to remove a non-existent item', () => {
    const controller = makeController()
    const item1 = {id: 1}
    const item2 = {id: 2}
    const item3 = {id: 3}
    store.commit('lists/example/setList', [item1, item2, item3])
    controller.remove({test: 4})
    expect(state.example.refs).toEqual(['1', '2', '3'])
  })
  it('Logs an error if attempting to replace a non-existent item', () => {
    mockError.mockImplementationOnce(() => undefined)
    const controller = makeController()
    const item1 = {id: 1, test: 'Hello'}
    const item2 = {id: 2, test: 'Goodbye'}
    const item3 = {id: 3, test: 'Aloha'}
    store.commit('lists/example/setList', [item1, item2, item3])
    const replacement = {id: 4, test: 'Surprise, Mothafucka'}
    controller.replace(replacement)
    expect(state.example.refs).toEqual(['1', '2', '3'])
    expect(mockError).toHaveBeenCalledWith(
      'Attempt to replace non-existent entry based on key \'id\':', replacement
    )
  })
  it('Fetches from the desired endpoint', () => {
    const controller = makeController()
    controller.get().then()
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'post', undefined, {params: {page: 1, size: 24}, cancelToken: expect.any(Object)})
    )
  })
  it('Sets from the resulting response', async() => {
    const controller = makeController()
    controller.get().then()
    const response = {
      results: [{test: 1}, {test: 2}],
      count: 2,
      size: 24,
    }
    mockAxios.mockResponse({
      status: 200,
      data: response,
    })
    await flushPromises()
    expect(state.example.response).toEqual({count: 2, size: 24})
  })
  it('Properly replaces old items in the response', async() => {
    const controller = makeController()
    controller.setList([{id: 1}, {id: 2}, {id: 3}, {id: 4}])
    controller.get().then()
    const response = {
      results: [{id: 3}, {id: 5}],
      count: 2,
      size: 24,
    }
    mockAxios.mockResponse({
      status: 200,
      data: response,
    })
    await flushPromises()
    expect(state.example.refs).toEqual(['3', '5'])
    expect(state.example.items['1']).toBe(undefined)
    expect(state.example.items['2']).toBe(undefined)
    expect(state.example.items['3'].x.id).toBe(3)
    expect(state.example.items['4']).toBe(undefined)
    expect(state.example.items['5'].x.id).toBe(5)
  })
  it('Grows the list', async() => {
    const controller = makeController({grow: true})
    controller.get().then()
    const item1 = {id: 1}
    const item2 = {id: 2}
    const item3 = {id: 3}
    const item4 = {id: 4}
    const item5 = {id: 5}
    store.commit('lists/example/setList', [item1, item2, item3])
    const response = {
      results: [item4, item5],
      count: 2,
      size: 24,
    }
    mockAxios.mockResponse({
      status: 200,
      data: response,
    })
    await flushPromises()
    expect(state.example.refs).toEqual(['1', '2', '3', '4', '5'])
  })
  it('Posts to the list', async() => {
    const controller = makeController()
    controller.post({}).then()
    expect(mockAxios.post).toHaveBeenCalledWith(...rq('/endpoint/', 'post', {}))
  })
  it('Posts, then pushes to the list', async() => {
    const controller = makeController()
    controller.postPush({})
    mockAxios.mockResponse(rs({id: 1}))
    await flushPromises()
    expect(controller.list[0]).toBeTruthy()
    expect((controller.list[0] as any).x.id).toBe(1)
  })
  it('Fetches the loading state', () => {
    const controller = makeController()
    expect(controller.fetching).toBe(false)
  })
  it('Sets and fetches the response', () => {
    const controller = makeController()
    controller.response = {count: 3, size: 10}
    expect(state.example.response).toEqual({count: 3, size: 10})
    expect(controller.response).toEqual({count: 3, size: 10})
  })
  it('Fetches the next page', () => {
    const controller = makeController()
    controller.response = {count: 30, size: 5}
    controller.setList([{id: 1}, {id: 2}, {id: 3}, {id: 4}, {id: 5}])
    controller.next().then(() => {
      expect(controller.currentPage).toBe(2)
      expect(controller.list.map((x) => x.x)).toEqual([
        {id: 6}, {id: 7}, {id: 8}, {id: 9}, {id: 10},
      ])
    })
    expect(mockAxios.get).toHaveBeenCalled()
    mockAxios.mockResponse(rs({
      results: [{id: 6}, {id: 7}, {id: 8}, {id: 9}, {id: 10}],
      count: 30,
      size: 5,
    }))
  })
  it('Does not refetch the page if told to get the current page', () => {
    const controller = makeController()
    controller.response = {count: 30, size: 5}
    controller.setList([{id: 1}, {id: 2}, {id: 3}, {id: 4}, {id: 5}])
    expect(controller.currentPage).toBe(1)
    controller.currentPage = 1
    expect(mockAxios.get).not.toHaveBeenCalled()
  })
  it('Determines whether more is available', async() => {
    const controller = makeController()
    controller.response = {count: 30, size: 5}
    expect(controller.moreAvailable).toBe(true)
    controller.currentPage = 2
    mockAxios.mockResponse(rs({
      results: [],
      count: 30,
      size: 5,
    }))
    await flushPromises()
    expect(controller.moreAvailable).toBe(true)
    controller.currentPage = 5
    mockAxios.mockResponse(rs({
      results: [],
      count: 30,
      size: 5,
    }))
    await flushPromises()
    expect(controller.moreAvailable).toBe(true)
    controller.currentPage = 6
    mockAxios.mockResponse(rs({
      results: [],
      count: 30,
      size: 5,
    }))
    await flushPromises()
    expect(controller.moreAvailable).toBe(false)
  })
  it('Handles a reversed endpoint', async() => {
    const controller = makeController({grow: true, reverse: true})
    controller.get().then(() => {
      expect(controller.list.map((x) => x.x)).toEqual([{id: 6}, {id: 7}, {id: 8}, {id: 9}, {id: 10}])
    })
    mockAxios.mockResponse(rs({
      results: [{id: 10}, {id: 9}, {id: 8}, {id: 7}, {id: 6}],
      count: 10,
      size: 5,
    }))
    await flushPromises()
    controller.currentPage += 1
    mockAxios.mockResponse(rs({
      results: [{id: 5}, {id: 4}, {id: 3}, {id: 2}, {id: 1}],
      count: 10,
      size: 5,
    }))
    await flushPromises()
    expect(controller.list.map((x) => x.x)).toEqual([
      {id: 1}, {id: 2}, {id: 3}, {id: 4}, {id: 5}, {id: 6}, {id: 7}, {id: 8}, {id: 9}, {id: 10},
    ])
  })
  it('Does nothing if we are already on the last page and try to go next.', () => {
    const controller = makeController()
    controller.response = {count: 2, size: 5}
    controller.next().then()
    expect(mockAxios.get).not.toHaveBeenCalled()
    expect(controller.currentPage).toBe(1)
  })
  it('Reports a verified empty list', () => {
    const controller = makeController()
    controller.ready = true
    expect(controller.empty).toBe(true)
  })
  it('Adds unique items to a list', () => {
    const controller = makeController()
    controller.ready = true
    controller.uniquePush({id: 1})
    expect(controller.list.length).toBe(1)
    controller.uniquePush({id: 1})
    expect(controller.list.length).toBe(1)
  })
  it('Retries a fetch if there was a previous failure', () => {
    const controller = makeController()
    store.commit('lists/example/setFailed', true)
    controller.retryGet().then()
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', undefined, {params: {size: 24, page: 1}, cancelToken: expect.any(Object)})
    )
  })
  it('Grows on command', async() => {
    const controller = makeController()
    controller.response = {count: 100, size: 10}
    controller.grower(true)
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', undefined, {params: {size: 24, page: 2}, cancelToken: expect.any(Object)})
    )
    mockAxios.reset()
    controller.grower(true)
    expect(mockAxios.get).not.toHaveBeenCalled()
  })
  it('Reports the count', async() => {
    const controller = makeController()
    controller.response = {count: 100, size: 10}
    expect(controller.count).toBe(100)
  })
  it('Manually sets a null response', async() => {
    const controller = makeController()
    controller.response = {count: 100, size: 10}
    controller.response = null
    expect(controller.response).toBe(null)
  })
  it('Handles a non-paginated list', async() => {
    const controller = makeController({paginated: false})
    controller.firstRun().then()
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', undefined, {cancelToken: expect.any(Object)})
    )
    mockAxios.mockResponse(rs([{id: 1}, {id: 2}]))
    await flushPromises()
    expect(controller.list.length).toBe(2)
  })
})
