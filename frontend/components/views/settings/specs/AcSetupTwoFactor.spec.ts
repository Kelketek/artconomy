import {Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify/lib'
import Vue from 'vue'
import {
  cleanUp,
  createVuetify,
  docTarget,
  flushPromises,
  rq,
  rs,
  setViewer,
  vueSetup,
  mount,
} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import AcSetupTwoFactor from '../AcSetupTwoFactor.vue'
import mockAxios from '@/__mocks__/axios'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('ac-setup-two-factor', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    jest.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Fetches the relevant 2FA data', async() => {
    mount(AcSetupTwoFactor, {localVue, store, vuetify, propsData: {username: 'Fox'}})
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/auth/two-factor/tg/', 'get'),
    )
    expect(mockAxios.get).toHaveBeenCalledWith(...rq(
      '/api/profiles/v1/account/Fox/auth/two-factor/totp/',
      'get',
      undefined,
      {params: {page: 1, size: 24}, cancelToken: expect.any(Object)}),
    )
  })
  it('Handles a missing Telegram 2FA', async() => {
    setViewer(store, genUser())
    mockError.mockImplementationOnce(() => undefined)
    wrapper = mount(AcSetupTwoFactor, {localVue, store, vuetify, propsData: {username: 'Fox'}})
    // Have to respond to the other request first.
    mockAxios.mockResponse(rs({results: [], count: 0, size: 0}))
    await jest.runAllTimers()
    await flushPromises()
    mockAxios.mockError({status: 404})
    await flushPromises()
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.tgDevice.x).toBe(null)
    expect(vm.tgDevice.ready).toBe(true)
  })
  it('Updates the relevant URLs', async() => {
    mockError.mockImplementationOnce(() => undefined)
    wrapper = mount(AcSetupTwoFactor, {localVue, store, vuetify, propsData: {username: 'Fox'}})
    const vm = wrapper.vm as any
    expect(vm.url).toBe('/api/profiles/v1/account/Fox/auth/two-factor/')
    wrapper.setProps({username: 'Vulpes'})
    await vm.$nextTick()
    expect(vm.url).toBe('/api/profiles/v1/account/Vulpes/auth/two-factor/')
  })
  it('Creates a Telegram Device', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcSetupTwoFactor,
      {localVue, store, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget()},
    )
    mockAxios.mockResponse(rs({results: [], count: 0, size: 0}))
    mockAxios.mockError({status: 404})
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.find('.setup-telegram').trigger('click')
    expect(mockAxios.put).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/auth/two-factor/tg/', 'put'),
    )
  })
  it('Creates a TOTP Device', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcSetupTwoFactor,
      {localVue, store, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget()},
    )
    const vm = wrapper.vm as any
    mockAxios.mockResponse(rs({results: [], count: 0, size: 0}))
    mockAxios.mockError({status: 404})
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.find('.setup-totp').trigger('click')
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/auth/two-factor/totp/', 'post', {name: 'Phone'}),
    )
  })
})
