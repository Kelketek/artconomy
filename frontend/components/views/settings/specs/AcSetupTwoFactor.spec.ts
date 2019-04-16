import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import Vue from 'vue'
import {flushPromises, rq, rs, vuetifySetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import AcSetupTwoFactor from '../AcSetupTwoFactor.vue'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {listRegistry, Lists} from '@/store/lists/registry'
import mockAxios from '@/__mocks__/axios'
import {Profiles} from '@/store/profiles/registry'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)
let store: ArtStore
let wrapper: Wrapper<Vue>

const mockError = jest.spyOn(console, 'error')

describe('ac-setup-two-factor', () => {
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    listRegistry.reset()
    mockAxios.reset()
    jest.useFakeTimers()
  })
  it('Fetches the relevant 2FA data', async() => {
    mount(AcSetupTwoFactor, {localVue, store, propsData: {username: 'Fox'}})
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/auth/two-factor/tg/', 'get')
    )
    expect(mockAxios.get).toHaveBeenCalledWith(...rq(
      '/api/profiles/v1/account/Fox/auth/two-factor/totp/',
      'get',
      undefined,
      {params: {page: 1, size: 20}, cancelToken: {}})
    )
  })
  it('Handles a missing Telegram 2FA', async() => {
    mockError.mockImplementationOnce(() => undefined)
    wrapper = mount(AcSetupTwoFactor, {localVue, store, propsData: {username: 'Fox'}})
    // Have to respond to the other request first.
    mockAxios.mockResponse(rs({results: [], count: 0, size: 0}))
    await jest.runAllTimers()
    await flushPromises()
    mockAxios.mockError({status: 404})
    await flushPromises()
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.tgDevice.x).toBe(false)
  })
  it('Updates the relevant URLs', async() => {
    mockError.mockImplementationOnce(() => undefined)
    wrapper = mount(AcSetupTwoFactor, {localVue, store, propsData: {username: 'Fox'}})
    const vm = wrapper.vm as any
    expect(vm.url).toBe(`/api/profiles/v1/account/Fox/auth/two-factor/`)
    wrapper.setProps({username: 'Vulpes'})
    expect(vm.url).toBe(`/api/profiles/v1/account/Vulpes/auth/two-factor/`)
  })
  it('Creates a Telegram Device', async() => {
    wrapper = mount(
      AcSetupTwoFactor,
      {localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true}
    )
    const vm = wrapper.vm as any
    mockAxios.mockResponse(rs({results: [], count: 0, size: 0}))
    mockAxios.mockError({status: 404})
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.find('.setup-telegram').trigger('click')
    expect(mockAxios.put).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/auth/two-factor/tg/', 'put')
    )
  })
  it('Creates a TOTP Device', async() => {
    wrapper = mount(
      AcSetupTwoFactor,
      {localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true}
    )
    const vm = wrapper.vm as any
    mockAxios.mockResponse(rs({results: [], count: 0, size: 0}))
    mockAxios.mockError({status: 404})
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.find('.setup-totp').trigger('click')
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Fox/auth/two-factor/totp/', 'post', {name: 'Phone'})
    )
  })
})
