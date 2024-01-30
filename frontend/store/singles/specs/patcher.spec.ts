import mockAxios from '@/specs/helpers/mock-axios'
import Patcher from '@/specs/helpers/dummy_components/patcher.vue'
import {VueWrapper} from '@vue/test-utils'
import flushPromises from 'flush-promises'
import {cleanUp, docTarget, mount, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import {errorSend} from '@/store/singles/patcher'
import {AxiosError} from 'axios'
import {VIEWER_TYPE} from '@/types/VIEWER_TYPE'
import Empty from '@/specs/helpers/dummy_components/empty'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {nextTick, toValue} from 'vue'

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
  test('Retrieves the initial value', async () => {
    wrapper = mount(Patcher, vueSetup({store}))
    await nextTick()
    expect(wrapper.vm.subjectHandler.user.patchers.sfw_mode.model).toBe(false)
    expect(wrapper.vm.subjectHandler.artistProfile.patchers.max_load.model).toBe(10)
  })
  test('Sends an appropriate patch request upon change', async() => {
    wrapper = mount(Patcher, vueSetup({store}))
    wrapper.vm.subjectHandler.user.patchers.sfw_mode.model = true
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
    wrapper.vm.subjectHandler.user.patchers.sfw_mode.model = true
    expect(wrapper.vm.subjectHandler.user.x.sfw_mode).toBe(false)
    expect(wrapper.vm.subjectHandler.user.patchers.sfw_mode.model).toBe(true)
  })
  test('Calls the appropriate callback when the patch has finished', async() => {
    wrapper = mount(Patcher, vueSetup({store}))
    const fakeUpdate = vi.spyOn((wrapper.vm as any).subjectHandler.user, 'updateX')
    expect(wrapper.vm.subjectHandler.user.patchers.sfw_mode.model).toBe(false);
    wrapper.vm.subjectHandler.user.patchers.sfw_mode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockAxios.mockResponse(rs({sfw_mode: true}))
    await flushPromises()
    expect(fakeUpdate).toHaveBeenCalledWith({sfw_mode: true})
    expect(fakeUpdate).toHaveBeenCalledTimes(1)
  })
  test('Properly reacts to upstream changes', async() => {
    const wrapper = mount(Patcher, vueSetup({store}))
    expect(wrapper.find('#sfw_mode').text()).toBe('false');
    (wrapper.vm as any).subjectHandler.user.patchers.sfw_mode.model = true
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).subjectHandler.user.patchers.sfw_mode.model).toBe(true)
    // This is where it fails.
    expect(wrapper.find('#sfw_mode').text()).toBe('true')
  })
  test('Stores errors for the field', async() => {
    wrapper = mount(Patcher, vueSetup({store}));
    wrapper.vm.subjectHandler.user.patchers.sfw_mode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockAxios.mockError({response: rs({sfw_mode: ['Porn is essential!']})})
    await flushPromises()
    expect(mockError).not.toHaveBeenCalled()
    expect(toValue(wrapper.vm.subjectHandler.user.patchers.sfw_mode.errors)).toEqual(['Porn is essential!'])
  })
  test('Stores errors for server errors', async() => {
    wrapper = mount(Patcher, vueSetup({store}));
    (wrapper.vm as any).subjectHandler.user.patchers.sfw_mode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockAxios.mockError({response: rs({detail: 'Nope.'})})
    await flushPromises()
    expect(toValue((wrapper.vm as any).subjectHandler.user.patchers.sfw_mode.errors)).toEqual(['Nope.'])
  })
  test('Stores an error if we do not know what happened', async() => {
    mount(Empty, vueSetup({store}))
    wrapper = mount(Patcher, vueSetup({store}));
    (wrapper.vm as any).subjectHandler.user.patchers.sfw_mode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockTrace.mockImplementation(() => undefined)
    mockAxios.mockError({})
    await flushPromises()
    // deriveErrors will also call it.
    expect(toValue((wrapper.vm as any).subjectHandler.user.patchers.sfw_mode.errors)).toEqual(
      ['We had an issue contacting the server. Please try again later!'],
    )
  })
  test('Stores an error if the server times out', async() => {
    wrapper = mount(Patcher, vueSetup({store}));
    (wrapper.vm as any).subjectHandler.user.patchers.sfw_mode.model = true
    await flushPromises()
    vi.runAllTimers()
    mockTrace.mockImplementation(() => undefined)
    mockAxios.mockError({code: 'ECONNABORTED'})
    await flushPromises()
    // deriveErrors will also call it.
    expect(toValue((wrapper.vm as any).subjectHandler.user.patchers.sfw_mode.errors)).toEqual(
      ['Timed out or aborted. Please try again or contact support!'],
    )
  })
  test('Ignores axios cancel errors', () => {
    mockError.mockClear()
    mockTrace.mockClear()
    wrapper = mount(Patcher, vueSetup({store}))
    errorSend((wrapper.vm as any).subjectHandler.user.patchers.sfw_mode)({config: {}, __CANCEL__: true} as unknown as AxiosError)
    expect(mockTrace).not.toHaveBeenCalled()
    expect(mockError).not.toHaveBeenCalled()
    expect(toValue((wrapper.vm as any).subjectHandler.user.patchers.sfw_mode.errors)).toEqual([])
  })
})
