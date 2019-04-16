import Vue from 'vue'
import Vuex from 'vuex'
import mockAxios from '@/specs/helpers/mock-axios'
import Patcher from '@/specs/helpers/dummy_components/patcher.vue'
import PatcherBroken from '@/specs/helpers/dummy_components/patcher-broken.vue'
import {createLocalVue, mount, shallowMount, Wrapper} from '@vue/test-utils'
import flushPromises from 'flush-promises'
import {rq, rs, setViewer} from '@/specs/helpers'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import PatcherNonExist from '@/specs/helpers/dummy_components/patcher-non-exist.vue'
import {errorSend} from '@/store/singles/patcher'
import {AxiosError} from 'axios'
import {Lists} from '@/store/lists/registry'

Vue.use(Vuex)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)
let store: ArtStore
const mockWarn = jest.spyOn(console, 'warn')
const mockError = jest.spyOn(console, 'error')
const mockTrace = jest.spyOn(console, 'trace')
jest.useFakeTimers()

describe('Patcher', () => {
  let wrapper: Wrapper<Vue>
  let wrapper2: Wrapper<Vue>
  beforeEach(() => {
    mockAxios.reset()
    mockWarn.mockClear()
    mockError.mockClear()
    mockTrace.mockClear()
    jest.clearAllTimers()
    if (wrapper) {
      wrapper.destroy()
    }
    singleRegistry.reset()
    store = createStore()
    setViewer(store, genUser())
  })
  it('Retrieves the initial value', () => {
    wrapper = mount(Patcher, {localVue, store})
    expect((wrapper.vm as any).sfwMode.model).toBe(false)
    expect((wrapper.vm as any).maxLoad.model).toBe(10)
  })
  it('Sends an appropriate patch request upon change', async() => {
    wrapper = mount(Patcher, {localVue, store});
    (wrapper.vm as any).sfwMode.model = true
    jest.runAllTimers()
    expect(mockAxios.patch).toHaveBeenCalledTimes(1)
    const request = rq(
      '/api/profiles/v1/account/Fox/',
      'patch', {sfw_mode: true}
    )
    request[2].cancelToken = {}
    expect(mockAxios.patch).toHaveBeenCalledWith(...request)
  })
  it('Returns a dirty value until the patch has settled', async() => {
    wrapper = mount(Patcher, {localVue, store});
    (wrapper.vm as any).sfwMode.model = true
    expect((wrapper.vm as any).subjectHandler.user.x.sfw_mode).toBe(false)
    expect((wrapper.vm as any).sfwMode.model).toBe(true)
  })
  it('Calls the appropriate callback when the patch has finished', async() => {
    wrapper = mount(Patcher, {localVue, store})
    const fakeUpdate = jest.spyOn((wrapper.vm as any).subjectHandler.user, 'updateX')
    expect((wrapper.vm as any).sfwMode.model).toBe(false);
    (wrapper.vm as any).sfwMode.model = true
    await flushPromises()
    jest.runAllTimers()
    mockAxios.mockResponse(rs({sfw_mode: true}))
    await flushPromises()
    expect(fakeUpdate).toHaveBeenCalledWith({sfw_mode: true})
    expect(fakeUpdate).toHaveBeenCalledTimes(1)
  })
  it('Does not share cache state between multiple instances', async() => {
    wrapper = mount(Patcher, {localVue, store})
    wrapper2 = mount(Patcher, {localVue, store});
    (wrapper.vm as any).sfwMode.model = false;
    (wrapper2.vm as any).sfwMode.model = false
    expect((wrapper.vm as any).sfwMode.model).toBe(false)
    expect((wrapper.vm as any).maxLoad.model).toBe(10)
    expect((wrapper2.vm as any).sfwMode.model).toBe(false);
    (wrapper.vm as any).sfwMode.model = true
    expect((wrapper.vm as any).sfwMode.model).toBe(true)
    expect((wrapper2.vm as any).sfwMode.model).toBe(false)
    expect((wrapper.vm as any).maxLoad.model).toBe(10)
    expect((wrapper2.vm as any).maxLoad.model).toBe(10)
  })
  // Reactivity broken for test lib? This works in real application.
  // it('Properly reacts to upstream changes', async () => {
  //   const wrapper = mount(Patcher, {localVue, sync: false, attachToDocument: true})
  //   expect(wrapper.find('#sfw_mode').text()).toBe('false');
  //   (wrapper.vm as any).subject.sfw_mode = true
  //   await wrapper.vm.$nextTick()
  //   expect((wrapper.vm as any).sfwMode).toBe(true)
  //   // This is where it fails.
  //   expect(wrapper.find('#sfw_mode').text()).toBe('true')
  // })
  it('Gives a warning when using a nonsense model on a patcher', async() => {
    mockWarn.mockImplementationOnce(() => undefined)
    wrapper = shallowMount(PatcherBroken, {localVue, store})
    expect((wrapper.vm as any).sfwMode.model).toBe(undefined)
    expect(mockWarn).toHaveBeenCalledWith(
      'Expected object in property named \'subjectHandler.user\', got ', undefined, ' instead.')
  })
  it('Alerts us when setting a field on a nonsense model on a patcher', async() => {
    mockWarn.mockImplementationOnce(() => undefined)
    wrapper = shallowMount(PatcherBroken, {localVue, store, sync: false, attachToDocument: true})
    mockError.mockImplementationOnce(() => undefined)
    expect((wrapper.vm as any).sfwMode.model).toBe(undefined);
    (wrapper.vm as any).sfwMode.model = true
    await flushPromises()
    jest.runAllTimers()
    expect(mockError).toHaveBeenCalledWith(Error('Cannot set undefined key on model: sfw_mode'))
  })
  it('Alerts us if we are trying to get a property which does not exist', async() => {
    mockError.mockImplementationOnce(() => undefined)
    wrapper = shallowMount(PatcherNonExist, {localVue, store, sync: false, attachToDocument: true})
    expect((wrapper.vm as any).maxLoad.model).toBe(undefined)
    expect(mockError).toHaveBeenCalledWith(
      `"max_load" is undefined on model "subjectHandler.user"`)
  })
  it('Alerts us if we are trying to set a property which does not exist', async() => {
    mockError.mockImplementationOnce(() => undefined)
    wrapper = shallowMount(PatcherNonExist, {localVue, store, sync: false, attachToDocument: true})
    mockError.mockClear()
    mockError.mockImplementationOnce(() => undefined);
    (wrapper.vm as any).maxLoad.model = 100
    await flushPromises()
    jest.runAllTimers()
    expect(mockError).toHaveBeenCalledWith(Error('Cannot set undefined key on model: max_load'))
  })
  it('Stores errors for the field', async() => {
    wrapper = mount(Patcher, {localVue, store, sync: false, attachToDocument: true});
    (wrapper.vm as any).sfwMode.model = true
    await flushPromises()
    jest.runAllTimers()
    mockAxios.mockError({response: rs({sfw_mode: ['Porn is essential!']})})
    await flushPromises()
    expect(mockError).not.toHaveBeenCalled()
    expect((wrapper.vm as any).sfwMode.errors).toEqual(['Porn is essential!'])
  })
  it('Stores errors for server errors', async() => {
    wrapper = mount(Patcher, {localVue, store, sync: false, attachToDocument: true});
    (wrapper.vm as any).sfwMode.model = true
    await flushPromises()
    jest.runAllTimers()
    mockAxios.mockError({response: rs({detail: 'Nope.'})})
    await flushPromises()
    expect((wrapper.vm as any).sfwMode.errors).toEqual(['Nope.'])
  })
  it('Stores an error if the server does not respond at all', async() => {
    wrapper = mount(Patcher, {localVue, store, sync: false, attachToDocument: true});
    (wrapper.vm as any).sfwMode.model = true
    await flushPromises()
    jest.runAllTimers()
    mockTrace.mockImplementation(() => undefined)
    mockAxios.mockError({})
    await flushPromises()
    // deriveErrors will also call it.
    expect((wrapper.vm as any).sfwMode.errors).toEqual(
      ['We had an issue contacting the server. Please try again later!']
    )
  })
  it('Ignores axios cancel errors', () => {
    mockError.mockClear()
    mockTrace.mockClear()
    wrapper = mount(Patcher, {localVue, store, sync: false, attachToDocument: true})
    errorSend((wrapper.vm as any).sfwMode)({config: {}, __CANCEL__: true} as unknown as AxiosError)
    expect(mockTrace).not.toHaveBeenCalled()
    expect(mockError).not.toHaveBeenCalled()
    expect((wrapper.vm as any).sfwMode.errors).toEqual([])
  })
})
