import {ListModuleOpts} from '@/store/lists/types/ListModuleOpts'
import {SingleController} from '@/store/singles/controller'
import {ArtStore, createStore} from '@/store'
import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount} from '@vue/test-utils'
import {singleRegistry, Singles} from '@/store/singles/registry'
import mockAxios from '@/specs/helpers/mock-axios'
import {flushPromises, rq, rs} from '@/specs/helpers'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

let store: ArtStore
let state: any
Vue.use(Vuex)
const localVue = createLocalVue()
localVue.use(Singles)

const mockError = jest.spyOn(console, 'error')

declare interface TestType {
  stuff: string,
}

describe('Single controller', () => {
  function makeController(extra?: Partial<ListModuleOpts>) {
    if (extra === undefined) {
      extra = {}
    }
    return new SingleController<TestType>({
      store,
      propsData: {
        initName: 'example',
        schema: {...{endpoint: '/endpoint/'}, ...extra},
      },
      // eslint-disable-next-line new-cap
      extends: new localVue({store}).$options,
    }
    )
  }
  beforeEach(() => {
    singleRegistry.reset()
    store = createStore()
    state = (store.state as any).singles
    mockAxios.reset()
  })
  it('Creates a singles module upon invocation', async() => {
    makeController()
    expect(state.example).toBeTruthy()
    expect(state.example.endpoint).toBe('/endpoint/')
  })
  it('Sends a put request', async() => {
    const controller = makeController()
    // @ts-ignore
    mockAxios.put.mockImplementationOnce(mockAxios.post)
    controller.put().then()
    expect(mockAxios.put).toHaveBeenCalledWith(...rq('/endpoint/', 'put'))
  })
  it('Sets the result of a put request', async() => {
    const controller = makeController()
    controller.put().then()
    mockAxios.mockResponse(rs({id: 1}))
    await flushPromises()
    expect(controller.x).toEqual({id: 1})
  })
  it('Gets the endpoint', () => {
    const controller = makeController()
    expect(controller.endpoint).toBe('/endpoint/')
  })
  it('Sets the endpoint', () => {
    const controller = makeController()
    controller.endpoint = '/test/'
    expect(state.example.endpoint).toBe('/test/')
  })
  it('Fetches the item from the server', async() => {
    const controller = makeController()
    controller.get().then()
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/endpoint/', 'get'))
  })
  it('Retries fetching if it has not previously succeeded', async() => {
    const controller = makeController()
    store.commit('singles/example/setFailed', true)
    controller.retryGet().then()
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('/endpoint/', 'get'))
  })
  it('Sets the item from the server', async() => {
    const controller = makeController()
    controller.get().then()
    mockAxios.mockResponse(rs({id: 1}))
    await flushPromises()
    expect(controller.x).toEqual({id: 1})
  })
  it('Sends a patch request', () => {
    const controller = makeController()
    controller.patch({}).then()
    expect(mockAxios.patch).toHaveBeenCalledWith(...rq('/endpoint/', 'patch', {}))
  })
  it('Sets the result of a patch request', async() => {
    const controller = makeController()
    controller.patch({}).then()
    mockAxios.mockResponse(rs({id: 1}))
    await flushPromises()
    expect(controller.x).toEqual({id: 1})
  })
  it('Throws an error when trying to pull a controller from a non-existent cache', async() => {
    const component = mount(Empty, {localVue, store}).vm
    expect(() => { component.$getSingle('test') }).toThrow(
      Error("Attempt to pull a Single which does not exist, 'test', from cache.")
    )
  })
  it('Allows deletion of a single through the controller', async() => {
    const controller = makeController()
    expect(state.example.endpoint).toBe('/endpoint/')
    controller.purge()
    expect(state.example).toBe(undefined)
    controller.purge()
    expect(state.example).toBe(undefined)
  })
  it('Logs a useful error if registration fails', async() => {
    const controller = makeController()
    mockError.mockImplementationOnce(() => undefined)
    expect(() => {
      controller.register(['blank', 'fox'])
    }).toThrow(TypeError("Cannot read property 'addChild' of undefined"))
    expect(mockError).toHaveBeenCalledWith(
      'Failed registering ["blank","fox"].Likely, the parent path is not registered, but check error for ' +
      'more detail. It could also be an error in a watcher/computed property.'
    )
  })
  it('Returns an object from toJSON to prevent the testing pretty printer from hanging forever', async() => {
    const controller = makeController()
    expect(typeof controller.toJSON()).toBe('object')
  })
  it('Retrieves the fetching flag', () => {
    const controller = makeController()
    expect(controller.fetching).toBe(false)
  })
  it('Retrieves the failed flag', () => {
    const controller = makeController()
    expect(controller.failed).toBe(false)
  })
  it('Dynamically creates patchers', () => {
    const controller = makeController()
    controller.setX({stuff: 'Things'})
    expect(controller.patchers.stuff.model).toBe('Things')
    controller.patchers.stuff.rawSet('Wat')
    expect(mockAxios.patch).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', {stuff: 'Wat'}, {cancelToken: expect.any(Object)})
    )
  })
  it('Listens to a pattern', () => {
    const wrapper = mount(Empty, {localVue, store})
    const vm = wrapper.vm as any
    wrapper.vm.$listenForSingle('*')
    expect(singleRegistry.listeners['*']).toEqual([vm._uid])
    singleRegistry.ignore(vm._uid, '*')
    expect(singleRegistry.listeners['*']).toBe(undefined)
  })
  it('Sets the params', () => {
    const controller = makeController()
    controller.params = {wat: 'do'}
    expect(controller.params).toEqual({wat: 'do'})
    expect(state.example.params).toEqual({wat: 'do'})
    controller.params = null
    expect(controller.params).toBeNull()
    expect(state.example.params).toBeNull()
  })
  it('Refreshes the value', () => {
    const controller = makeController()
    controller.ready = true
    expect(controller.ready).toBe(true)
    const mockGet = jest.spyOn(controller, 'get')
    controller.refresh()
    expect(controller.ready).toBe(false)
    expect(mockGet).toHaveBeenCalled()
  })
})
