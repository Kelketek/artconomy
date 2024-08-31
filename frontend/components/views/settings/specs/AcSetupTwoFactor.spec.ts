import {VueWrapper} from '@vue/test-utils'
import {cleanUp, flushPromises, mount, rq, rs, vueSetup, waitFor} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import AcSetupTwoFactor from '../AcSetupTwoFactor.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {genPricing} from '@/lib/specs/helpers.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import {nextTick} from 'vue'

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
    setViewer({ store, user: genUser() })
    mockError.mockImplementationOnce(() => undefined)
    wrapper = mount(AcSetupTwoFactor, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    const tgReq = mockAxios.getReqByMatchUrl(/[/]tg[/]/)
    mockAxios.mockError({status: 404}, tgReq)
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
    await nextTick()
    expect(vm.url).toBe('/api/profiles/account/Vulpes/auth/two-factor/')
  })
  test('Creates a Telegram Device', async() => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      AcSetupTwoFactor,
      {
        ...vueSetup({store}),
        props: {username: 'Fox'},
      },
    )
    wrapper.vm.tgDevice.makeReady(null)
    wrapper.vm.totpDevices.makeReady([])
    await waitFor(async () => await wrapper.find('.setup-telegram').trigger('click'))
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/auth/two-factor/tg/', 'put'),
    )
  })
  test('Creates a TOTP Device', async() => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      AcSetupTwoFactor,
      {
        ...vueSetup({store}),
        props: {username: 'Fox'},
      },
    )
    wrapper.vm.tgDevice.makeReady(null)
    wrapper.vm.totpDevices.makeReady([])
    await waitFor(async () => await wrapper.find('.setup-totp').trigger('click'))
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Fox/auth/two-factor/totp/', 'post', {name: 'Phone'}),
    )
  })
})
