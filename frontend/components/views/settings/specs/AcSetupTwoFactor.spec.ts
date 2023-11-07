import {VueWrapper} from '@vue/test-utils'
import {cleanUp, flushPromises, mount, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import AcSetupTwoFactor from '../AcSetupTwoFactor.vue'
import mockAxios from '@/__mocks__/axios'
import {genUser} from '@/specs/helpers/fixtures'
import {genPricing} from '@/lib/specs/helpers'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

const mockError = vi.spyOn(console, 'error')

describe('ac-setup-two-factor', () => {
  beforeEach(() => {
    store = createStore()
    vi.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Fetches the relevant 2FA data', async() => {
    mount(AcSetupTwoFactor, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/auth/two-factor/tg/', 'get'),
    )
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/account/Fox/auth/two-factor/totp/',
      'get',
      undefined,
      {
        params: {
          page: 1,
          size: 24,
        },
        signal: expect.any(Object),
      }),
    )
  })
  test('Handles a missing Telegram 2FA', async() => {
    setViewer(store, genUser())
    mockError.mockImplementationOnce(() => undefined)
    wrapper = mount(AcSetupTwoFactor, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    // Have to respond to the other requests first.
    mockAxios.mockResponse(rs(genPricing()))
    mockAxios.mockResponse(rs({
      results: [],
      count: 0,
      size: 0,
    }))
    vi.runAllTimers()
    await flushPromises()
    mockAxios.mockError({status: 404})
    await flushPromises()
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.tgDevice.x).toBe(null)
    expect(vm.tgDevice.ready).toBe(true)
  })
  test('Updates the relevant URLs', async() => {
    mockError.mockImplementationOnce(() => undefined)
    wrapper = mount(AcSetupTwoFactor, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    expect(vm.url).toBe('/api/profiles/account/Fox/auth/two-factor/')
    await wrapper.setProps({username: 'Vulpes'})
    await vm.$nextTick()
    expect(vm.url).toBe('/api/profiles/account/Vulpes/auth/two-factor/')
  })
  test('Creates a Telegram Device', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcSetupTwoFactor,
      {
        ...vueSetup({store}),
        props: {username: 'Fox'},
      },
    )
    mockAxios.mockResponse(rs(genPricing()))
    mockAxios.mockResponse(rs({
      results: [],
      count: 0,
      size: 0,
    }))
    mockAxios.mockError({status: 404})
    await flushPromises()
    await wrapper.vm.$nextTick()
    await wrapper.find('.setup-telegram').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/auth/two-factor/tg/', 'put'),
    )
  })
  test('Creates a TOTP Device', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcSetupTwoFactor,
      {
        ...vueSetup({store}),
        props: {username: 'Fox'},
      },
    )
    mockAxios.mockResponse(rs(genPricing()))
    mockAxios.mockResponse(rs({
      results: [],
      count: 0,
      size: 0,
    }))
    mockAxios.mockError({status: 404})
    await flushPromises()
    await wrapper.vm.$nextTick()
    await wrapper.find('.setup-totp').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/auth/two-factor/totp/', 'post', {name: 'Phone'}),
    )
  })
})
