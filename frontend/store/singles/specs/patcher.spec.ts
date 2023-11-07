import mockAxios from '@/specs/helpers/mock-axios'
import Patcher from '@/specs/helpers/dummy_components/patcher.vue'
import PatcherBroken from '@/specs/helpers/dummy_components/patcher-broken.vue'
import {shallowMount, VueWrapper} from '@vue/test-utils'
import flushPromises from 'flush-promises'
import {cleanUp, docTarget, mount, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import PatcherNonExist from '@/specs/helpers/dummy_components/patcher-non-exist.vue'
import {errorSend} from '@/store/singles/patcher'
import {AxiosError} from 'axios'
import {VIEWER_TYPE} from '@/types/VIEWER_TYPE'
import Empty from '@/specs/helpers/dummy_components/empty'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

const localVue = vueSetup()
let store: ArtStore
const mockWarn = vi.spyOn(console, 'warn')
const mockError = vi.spyOn(console, 'error')
const mockTrace = vi.spyOn(console, 'trace')

describe('Patcher', () => {
  let wrapper: VueWrapper<any>
  let wrapper2: VueWrapper<any>
  beforeEach(() => {
    vi.useFakeTimers()
    mockWarn.mockClear()
    mockError.mockClear()
    mockTrace.mockClear()
    vi.clearAllTimers()
    store = createStore()
    setViewer(store, genUser())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Retrieves the initial value', () => {
    wrapper = mount(Patcher, vueSetup({store}))
    expect(wrapper.vm.sfwMode.model).toBe(false)
    expect(wrapper.vm.maxLoad.model).toBe(10)
  })
  test('Sends an appropriate patch request upon change', async() => {
    wrapper = mount(Patcher, vueSetup({store}))
    wrapper.vm.sfwMode.model = true
    vi.runAllTimers()
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    const request = rq(
      '/api/profiles/account/Fox/',
      'patch', {sfw_mode: true},
    )
    expect(mockAxios.request).toHaveBeenCalledWith(request)
  })
  test('Does not send a patch request when the url is #', async() => {
    wrapper = mount(Patcher, vueSetup({store}))
    wrapper.vm.localShare.makeReady({
      viewerType: VIEWER_TYPE.BUYER,
      showPayment: false,
      showAddSubmission: false,
    })
    await wrapper.vm.$nextTick();
    wrapper.vm.localShare.patchers.showPayment.model = true
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    expect(mockAxios.request).not.toHaveBeenCalled()
  })
  test('Returns a dirty value until the patch has settled', async() => {
    wrapper = mount(Patcher, vueSetup({store}))
    wrapper.vm.sfwMode.model = true
    expect(wrapper.vm.subjectHandler.user.x.sfw_mode).toBe(false)
    expect(wrapper.vm.sfwMode.model).toBe(true)
  })
  test('Calls the appropriate callback when the patch has finished', async() => {
    wrapper = mount(Patcher, vueSetup({store}))
    const fakeUpdate = vi.spyOn((wrapper.vm as any).subjectHandler.user, 'updateX')
    expect(wrapper.vm.sfwMode.model).toBe(false);
    wrapper.vm.sfwMode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockAxios.mockResponse(rs({sfw_mode: true}))
    await flushPromises()
    expect(fakeUpdate).toHaveBeenCalledWith({sfw_mode: true})
    expect(fakeUpdate).toHaveBeenCalledTimes(1)
  })
  test('Does not share cache state between multiple instances', async() => {
    const options = vueSetup({store})
    wrapper = mount(Patcher, options)
    wrapper2 = mount(Patcher, {...options, attachTo: docTarget()});
    wrapper.vm.sfwMode.model = false
    wrapper2.vm.sfwMode.model = false
    expect(wrapper.vm.sfwMode.model).toBe(false)
    expect(wrapper.vm.maxLoad.model).toBe(10)
    expect(wrapper2.vm.sfwMode.model).toBe(false);
    expect(wrapper.vm.sfwMode).not.toBe((wrapper2.vm as any).sfwMode)
    wrapper.vm.sfwMode.model = true
    expect(wrapper.vm.sfwMode.model).toBe(true)
    expect(wrapper2.vm.sfwMode.model).toBe(false)
    expect(wrapper.vm.maxLoad.model).toBe(10)
    expect(wrapper2.vm.maxLoad.model).toBe(10)
  })
  test('Properly reacts to upstream changes', async() => {
    const wrapper = mount(Patcher, vueSetup({store}))
    expect(wrapper.find('#sfw_mode').text()).toBe('false');
    (wrapper.vm as any).sfwMode.model = true
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).sfwMode.model).toBe(true)
    // This is where it fails.
    expect(wrapper.find('#sfw_mode').text()).toBe('true')
  })
  test('Gives a warning when using a nonsense model on a patcher', async() => {
    mockWarn.mockImplementation(() => undefined)
    wrapper = shallowMount(PatcherBroken, vueSetup({store}))
    expect((wrapper.vm as any).sfwMode.model).toBe(undefined)
    expect(mockWarn).toHaveBeenCalledWith(
      'Expected object in property named \'subjectHandler.user\', got ', undefined, ' instead.')
  })
  test('Alerts us when setting a field on a nonsense model on a patcher', async() => {
    mockWarn.mockImplementation(() => undefined)
    wrapper = shallowMount(PatcherBroken, vueSetup({store}))
    mockError.mockImplementation(() => undefined)
    expect((wrapper.vm as any).sfwMode.model).toBe(undefined);
    (wrapper.vm as any).sfwMode.model = true
    await flushPromises()
    vi.runAllTimers()
    expect(mockError).toHaveBeenCalledWith(Error('Cannot set undefined key on model: sfw_mode'))
  })
  test('Alerts us if we are trying to get a property which does not exist', async() => {
    mockError.mockImplementationOnce(() => undefined)
    wrapper = shallowMount(PatcherNonExist, vueSetup({store}))
    expect(wrapper.vm.maxLoad.model).toBe(undefined)
    expect(mockError).toHaveBeenCalledWith(
      '"max_load" is undefined on model "subjectHandler.user"')
  })
  test('Alerts us if we are trying to set a property which does not exist', async() => {
    mockError.mockImplementationOnce(() => undefined)
    wrapper = shallowMount(PatcherNonExist, vueSetup({store}))
    mockError.mockClear()
    mockError.mockImplementationOnce(() => undefined);
    (wrapper.vm as any).maxLoad.model = 100
    await flushPromises()
    vi.runAllTimers()
    expect(mockError).toHaveBeenCalledWith(Error('Cannot set undefined key on model: max_load'))
  })
  test('Stores errors for the field', async() => {
    wrapper = mount(Patcher, vueSetup({store}));
    wrapper.vm.sfwMode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockAxios.mockError({response: rs({sfw_mode: ['Porn is essential!']})})
    await flushPromises()
    expect(mockError).not.toHaveBeenCalled()
    expect(wrapper.vm.sfwMode.errors).toEqual(['Porn is essential!'])
  })
  test('Stores errors for server errors', async() => {
    wrapper = mount(Patcher, vueSetup({store}));
    (wrapper.vm as any).sfwMode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockAxios.mockError({response: rs({detail: 'Nope.'})})
    await flushPromises()
    expect((wrapper.vm as any).sfwMode.errors).toEqual(['Nope.'])
  })
  test('Stores an error if we do not know what happened', async() => {
    mount(Empty, vueSetup({store}))
    wrapper = mount(Patcher, vueSetup({store}));
    (wrapper.vm as any).sfwMode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockTrace.mockImplementation(() => undefined)
    mockAxios.mockError({})
    await flushPromises()
    // deriveErrors will also call it.
    expect((wrapper.vm as any).sfwMode.errors).toEqual(
      ['We had an issue contacting the server. Please try again later!'],
    )
  })
  test('Stores an error if the server times out', async() => {
    wrapper = mount(Patcher, vueSetup({store}));
    (wrapper.vm as any).sfwMode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockTrace.mockImplementation(() => undefined)
    mockAxios.mockError({code: 'ECONNABORTED'})
    await flushPromises()
    // deriveErrors will also call it.
    expect((wrapper.vm as any).sfwMode.errors).toEqual(
      ['Timed out or aborted. Please try again or contact support!'],
    )
  })
  test('Ignores axios cancel errors', () => {
    mockError.mockClear()
    mockTrace.mockClear()
    wrapper = mount(Patcher, vueSetup({store}))
    errorSend((wrapper.vm as any).sfwMode)({config: {}, __CANCEL__: true} as unknown as AxiosError)
    expect(mockTrace).not.toHaveBeenCalled()
    expect(mockError).not.toHaveBeenCalled()
    expect((wrapper.vm as any).sfwMode.errors).toEqual([])
  })
})
