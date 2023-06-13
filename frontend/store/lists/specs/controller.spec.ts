import {ListController} from '../controller'
import {listRegistry} from '../registry'
import {ArtStore, createStore} from '../../index'
import {Wrapper} from '@vue/test-utils'
import mockAxios from '@/specs/helpers/mock-axios'
import Vue, {VueConstructor} from 'vue'
import {rq, rs, mount, cleanUp, vueSetup} from '@/specs/helpers'
import flushPromises from 'flush-promises'
import {ListModuleOpts} from '../types/ListModuleOpts'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {SingleController} from '@/store/singles/controller'
import WS from 'jest-websocket-mock'
import {ListSocketSettings} from '@/store/lists/types/ListSocketSettings'
import {cloneDeep} from 'lodash'

let store: ArtStore
let state: any
let empty: Wrapper<Vue>
let socketSettings: ListSocketSettings
let localVue: VueConstructor

const mockWarning = jest.spyOn(console, 'warn')

describe('List controller', () => {
  function makeController(extra?: Partial<ListModuleOpts>) {
    const schema = {...{endpoint: '/endpoint/'}, ...extra}
    return empty.vm.$getList('example', schema)
  }

  beforeEach(() => {
    localVue = vueSetup()
    store = createStore()
    state = (store.state as any).lists
    empty = mount(Empty, {localVue, store})
    socketSettings = {
      appLabel: 'sales',
      modelName: 'LineItem',
      serializer: 'LineItemSerializer',
      list: {
        listName: 'line_items',
        pk: '100',
        appLabel: 'sales',
        modelName: 'Deliverable',
      },
    }
  })
  afterEach(() => {
    cleanUp()
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
    const controller = makeController({params: {size: 5}})
    expect(controller.pageSize).toBe(5)
  })
  it('Retrieves the page number', () => {
    const controller = makeController({params: {page: 5}})
    expect(controller.currentPage).toBe(5)
    controller.params = {}
    expect(controller.currentPage).toBe(1)
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
    expect(controller.params).toEqual({stuff: 'things', wat: 'do', page: 1, size: 24})
    controller.params = {dude: 'sweet'}
    expect(controller.params).toEqual({dude: 'sweet', page: 1, size: 24})
    controller.params = null
    expect(controller.params).toEqual({page: 1, size: 24})
  })
  it('Grabs and sets the params without pagination', () => {
    const controller = makeController({params: {stuff: 'things', wat: 'do'}, paginated: false})
    expect(controller.params).toEqual({stuff: 'things', wat: 'do'})
    controller.params = {dude: 'sweet', page: 2}
    expect(controller.params).toEqual({dude: 'sweet', page: 2})
    controller.params = null
    expect(controller.params).toEqual(null)
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
  it('Unshifts onto the beginning of the list', () => {
    const controller = makeController()
    const item1 = {id: 2, test: 'Hello'}
    const item2 = {id: 3, test: 'Goodbye'}
    const item3 = {id: 4, test: 'Aloha'}
    store.commit('lists/example/setList', [item1, item2, item3])
    const item4 = {id: 1, test: 'Surprise, Mothafucka'}
    controller.unshift(item4)
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
  it('Fetches from the desired endpoint', () => {
    const controller = makeController()
    controller.get().then()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/endpoint/', 'get', undefined, {params: {page: 1, size: 24}, cancelToken: expect.any(Object)}),
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
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/endpoint/', 'post', {}))
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
  it('Listens for a list', async() => {
    const wrapper = mount(Empty, {localVue, store})
    const vm = wrapper.vm as any
    wrapper.vm.$listenForList('testList')
    expect(listRegistry.listeners.testList).toEqual([vm._uid])
    const otherWrapper = mount(Empty, {localVue, store})
    otherWrapper.vm.$getList('testList', {endpoint: '/'}).setList([{id: 1}, {id: 2}, {id: 3}])
    await vm.$nextTick()
    otherWrapper.destroy()
    await wrapper.vm.$nextTick()
    expect(
      wrapper.vm.$getList('testList').list.map((item: SingleController<any>) => item.x),
    ).toEqual([{id: 1}, {id: 2}, {id: 3}])
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
    expect(mockAxios.request).toHaveBeenCalled()
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
    expect(mockAxios.request).not.toHaveBeenCalled()
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
    expect(mockAxios.request).not.toHaveBeenCalled()
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
    controller.uniquePush({id: 1, text: 'other'})
    expect(controller.list.length).toBe(1)
  })
  it('Retries a fetch if there was a previous failure', () => {
    const controller = makeController()
    store.commit('lists/example/setFailed', true)
    controller.retryGet().then()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/endpoint/', 'get', undefined, {params: {size: 24, page: 1}, cancelToken: expect.any(Object)}),
    )
  })
  it('Grows on command', async() => {
    const controller = makeController()
    controller.response = {count: 100, size: 10}
    controller.grower(true)
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/endpoint/', 'get', undefined, {params: {size: 24, page: 2}, cancelToken: expect.any(Object)}),
    )
    mockAxios.reset()
    controller.grower(true)
    expect(mockAxios.request).not.toHaveBeenCalled()
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
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/endpoint/', 'get', undefined, {cancelToken: expect.any(Object)}),
    )
    mockAxios.mockResponse(rs([{id: 1}, {id: 2}]))
    await flushPromises()
    expect(controller.list.length).toBe(2)
  })
  it('Receives new items from the server.', async() => {
    const controller = makeController({socketSettings})
    const server = new WS(controller.$sock.endpoint, {jsonProtocol: true})
    controller.$root.$sock.open()
    controller.makeReady([])
    await server.connected
    await controller.$nextTick()
    // await expect(server).toReceiveMessage()
    server.send({command: 'sales.Deliverable.pk.100.line_items.LineItemSerializer.new', payload: {id: 5, name: 'stuff'}})
    await controller.$nextTick()
    expect(controller.list[0].x.name).toBe('stuff')
    const mockSend = jest.spyOn(controller.$sock, 'send')
    controller.purge()
    // The mock socket doesn't recognize this as being sent no matter what I do, so capturing it here.
    expect(mockSend).toHaveBeenCalledWith(
      'clear_watch_new',
      {
        app_label: 'sales',
        model_name: 'Deliverable',
        pk: '100',
        list_name: 'line_items',
        serializer: 'LineItemSerializer',
      },
    )
  })
  it('Receives new items from the server, sans primary key.', async() => {
    const settings = cloneDeep(socketSettings)
    delete settings.list.pk
    const controller = makeController({socketSettings: settings})
    const server = new WS(controller.$sock.endpoint, {jsonProtocol: true})
    controller.$root.$sock.open()
    controller.makeReady([])
    await server.connected
    await controller.$nextTick()
    // await expect(server).toReceiveMessage()
    server.send({command: 'sales.Deliverable.line_items.LineItemSerializer.new', payload: {id: 5, name: 'stuff'}})
    await controller.$nextTick()
    expect(controller.list[0].x.name).toBe('stuff')
    const mockSend = jest.spyOn(controller.$sock, 'send')
    controller.purge()
    // The mock socket doesn't recognize this as being sent no matter what I do, so capturing it here.
    expect(mockSend).toHaveBeenCalledWith(
      'clear_watch_new',
      {
        app_label: 'sales',
        model_name: 'Deliverable',
        list_name: 'line_items',
        serializer: 'LineItemSerializer',
      },
    )
  })
  it('Detects if the content is stale and refetches upon reconnection.', async() => {
    const controller = makeController({socketSettings})
    controller.makeReady([])
    let server = new WS(controller.$sock.endpoint, {jsonProtocol: true})
    controller.$root.$sock.open()
    await server.connected
    await controller.$nextTick()
    await expect(server).toReceiveMessage({
      command: 'watch_new',
      payload: {
        app_label: 'sales',
        model_name: 'Deliverable',
        list_name: 'line_items',
        pk: '100',
        serializer: 'LineItemSerializer',
      },
    })
    controller.$sock.socket!.close()
    controller.$sock.endpoint = 'ws://localhost/boop/snoot'
    await server.close()
    await controller.$nextTick()
    expect(controller.stale).toBe(true)
    mockAxios.reset()
    WS.clean()
    await flushPromises()
    server = new WS(controller.$sock.endpoint, {jsonProtocol: true})
    await controller.$root.$sock.open()
    await server.connected
    await flushPromises()
    await controller.$nextTick()
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest.url).toBe('/endpoint/')
  })
  it('Reads and sets socket settings.', async() => {
    const controller = makeController()
    expect(controller.socketSettings).toBe(null)
    controller.socketSettings = socketSettings
    expect(controller.socketSettings).toEqual(socketSettings)
    expect(controller.attr('socketSettings')).toEqual(socketSettings)
  })
})
