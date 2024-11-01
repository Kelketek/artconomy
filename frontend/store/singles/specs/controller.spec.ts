import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {singleRegistry} from '@/store/singles/registry.ts'
import mockAxios from '@/specs/helpers/mock-axios.ts'
import {cleanUp, flushPromises, mount, rq, rs, vueSetup} from '@/specs/helpers/index.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import WS from 'vitest-websocket-mock'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {nextTick} from 'vue'
import type {SingleModuleOpts, SingleSocketSettings} from '@/store/singles/types.d.ts'

let store: ArtStore
let state: any
let empty: VueWrapper<any>
let socketSettings: SingleSocketSettings

const mockError = vi.spyOn(console, 'error')


describe('Single controller', () => {
  function makeController(extra?: Partial<SingleModuleOpts<any>>) {
    const schema = {...{endpoint: '/endpoint/'}, ...extra}
    return empty.vm.$getSingle('example', schema)
  }
  beforeEach(() => {
    socketSettings = {
      appLabel: 'boop', modelName: 'snoot', serializer: 'BoopSerializer',
    }
    store = createStore()
    state = (store.state as any).singles
    mockAxios.reset()
    empty = mount(Empty, vueSetup({store}))
  })
  afterEach(() => {
    cleanUp(empty)
  })
  test('Creates a singles module upon invocation', async() => {
    makeController()
    expect(state.example).toBeTruthy()
    expect(state.example.endpoint).toBe('/endpoint/')
  })
  test('Sends a put request', async() => {
    const controller = makeController()
    // @ts-ignore
    mockAxios.request.mockImplementationOnce(mockAxios.request)
    controller.put().then()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/endpoint/', 'put'))
  })
  test('Sets the result of a put request', async() => {
    const controller = makeController()
    controller.put().then()
    mockAxios.mockResponse(rs({id: 1}))
    await flushPromises()
    expect(controller.x).toEqual({id: 1})
  })
  test('Gets the endpoint', () => {
    const controller = makeController()
    expect(controller.endpoint).toBe('/endpoint/')
  })
  test('Sets the endpoint', () => {
    const controller = makeController()
    controller.endpoint = '/test/'
    expect(state.example.endpoint).toBe('/test/')
  })
  test('Gets the socket settings', () => {
    const controller = makeController({socketSettings})
    expect(controller.socketSettings).toEqual(socketSettings)
  })
  test('Sets the socket settings', () => {
    const controller = makeController()
    controller.socketSettings = socketSettings
    expect(state.example.socketSettings).toEqual(socketSettings)
  })
  test('Generates socket update parameters', () => {
    const controller = makeController({socketSettings, x: {id: 5}})
    expect(controller.socketUpdateParams).toEqual({
      app_label: 'boop', model_name: 'snoot', serializer: 'BoopSerializer', pk: '5',
    })
  })
  test('Returns null if no pk can be derived', () => {
    const socketSettings = {
      appLabel: 'boop', modelName: 'snoot', serializer: 'BoopSerializer',
    }
    const controller = makeController({socketSettings, x: null})
    expect(controller.socketUpdateParams).toBe(null)
  })
  test('Fetches the item from the server', async() => {
    const controller = makeController()
    controller.get().then()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/endpoint/', 'get'))
  })
  test('Retries fetching if it has not previously succeeded', async() => {
    const controller = makeController()
    store.commit('singles/example/setFailed', true)
    controller.retryGet().then()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/endpoint/', 'get'))
  })
  test('Sets the item from the server', async() => {
    const controller = makeController()
    controller.get().then()
    mockAxios.mockResponse(rs({id: 1}))
    await flushPromises()
    expect(controller.x).toEqual({id: 1})
  })
  test('Sends a patch request', () => {
    const controller = makeController()
    controller.patch({}).then()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/endpoint/', 'patch', {}))
  })
  test('Sets the result of a patch request', async() => {
    const controller = makeController()
    controller.patch({}).then()
    mockAxios.mockResponse(rs({id: 1}))
    await flushPromises()
    expect(controller.x).toEqual({id: 1})
  })
  test('Throws an error when trying to pull a controller from a non-existent cache', async() => {
    const component = mount(Empty, vueSetup({store})).vm
    expect(() => { component.$getSingle('test') }).toThrow(
      Error("Attempt to pull a Single which does not exist, 'test', from cache."),
    )
  })
  test('Allows deletion of a single through the controller', async() => {
    const controller = makeController()
    expect(state.example.endpoint).toBe('/endpoint/')
    controller.purge()
    expect(state.example).toBe(undefined)
    controller.purge()
    expect(state.example).toBe(undefined)
  })
  test('Logs a useful error if registration fails', async() => {
    const controller = makeController()
    mockError.mockImplementationOnce(() => undefined)
    expect(() => {
      controller.register(['blank', 'fox'])
    }).toThrow(TypeError("Cannot read properties of undefined (reading 'addChild')"))
    expect(mockError).toHaveBeenCalledWith(
      'Failed registering ["blank","fox"].Likely, the parent path is not registered, but check error for ' +
      'more detail. It could also be an error in a watcher/computed property.',
    )
  })
  test('Returns an object from toJSON to prevent the testing pretty printer from hanging forever', async() => {
    const controller = makeController()
    expect(typeof controller.toJSON()).toBe('object')
  })
  test('Retrieves the fetching flag', () => {
    const controller = makeController()
    expect(controller.fetching).toBe(false)
  })
  test('Retrieves the failed flag', () => {
    const controller = makeController()
    expect(controller.failed).toBe(false)
  })
  test('Dynamically creates patchers', () => {
    const controller = makeController()
    controller.setX({stuff: 'Things'})
    expect(controller.patchers.stuff.model).toBe('Things')
    controller.patchers.stuff.rawSet('Wat')
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/endpoint/', 'patch', {stuff: 'Wat'}),
    )
  })
  test('Listens for a pattern', () => {
    const wrapper = mount(Empty, vueSetup({store}))
    const vm = wrapper.vm as any
    wrapper.vm.$listenForSingle('*')
    expect(singleRegistry.listeners['*']).toEqual([vm._uid])
    singleRegistry.ignore(vm._uid, '*')
    expect(singleRegistry.listeners['*']).toBe(undefined)
  })
  test('Sets the params', () => {
    const controller = makeController()
    controller.params = {wat: 'do'}
    expect(controller.params).toEqual({wat: 'do'})
    expect(state.example.params).toEqual({wat: 'do'})
    controller.params = null
    expect(controller.params).toBeNull()
    expect(state.example.params).toBeNull()
  })
  test('Refreshes the value', () => {
    const controller = makeController()
    controller.ready = true
    expect(controller.ready).toBe(true)
    const mockGet = vi.spyOn(controller, 'get')
    controller.refresh()
    expect(controller.ready).toBe(false)
    expect(mockGet).toHaveBeenCalled()
  })
  test('Syncs with the server', async() => {
    const controller = makeController({socketSettings, x: {id: 5}})
    const server = new WS(controller.$sock.endpoint, {jsonProtocol: true})
    controller.$sock.open()
    await server.connected
    await expect(server).toReceiveMessage({
      command: 'watch', payload: {app_label: 'boop', model_name: 'snoot', pk: '5', serializer: 'BoopSerializer'},
    })
    server.send({command: 'boop.snoot.update.BoopSerializer.5', payload: {id: 5, name: 'stuff'}})
    await nextTick()
    expect(controller.x!.name).toBe('stuff')
    controller.purge()
    await expect(server).toReceiveMessage({
      command: 'clear_watch', payload: {app_label: 'boop', model_name: 'snoot', pk: '5', serializer: 'BoopSerializer'},
    })
  })
})
