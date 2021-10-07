import Vue from 'vue'
import {createVuetify, docTarget, rs, setViewer, vueSetup, mount, cleanUp} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import {genUser} from '@/specs/helpers/fixtures'
import mockAxios from '@/__mocks__/axios'
import flushPromises from 'flush-promises'
import Vuetify from 'vuetify/lib'
import AcBankToggleAuthorize from '@/components/fields/AcBankToggleAuthorize.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcBankToggleAuthorize.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcBankToggleAuthorize, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', value: 1},
        stubs: ['router-link'],
        attachTo: docTarget(),
      })
  })
  it('Changes the bank status setting', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcBankToggleAuthorize, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', value: 1},
        stubs: ['router-link'],
        attachTo: docTarget(),
      })
    const mockEmit = jest.spyOn(wrapper.vm, '$emit')
    wrapper.find('.no-us-account').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockEmit).toHaveBeenCalledWith('input', 2)
  })
  it('Adds a bank when the user has enough balance', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcBankToggleAuthorize, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', value: 1, manageBanks: true},
        stubs: ['router-link'],
        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    vm.banks.setList([])
    vm.banks.fetching = false
    vm.banks.ready = true
    vm.balance.makeReady({
      available: '5.00',
      escrow: '0.00',
      pending: '0.00',
    })
    await vm.$nextTick()
    expect(vm.canAddBank).toBe(false)
    vm.willIncurFee.makeReady({value: true})
    await flushPromises()
    mockAxios.reset()
    wrapper.find('.add-account').trigger('click')
    await vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    mockAxios.mockResponse(rs({id: 2, last_four: '1234', type: 0}))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.banks.list.length).toBe(1)
    expect(vm.banks.list[0].x.last_four).toBe('1234')
  })
  it('Adds a bank when the user will not incur a fee', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcBankToggleAuthorize, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', value: 1, manageBanks: true},
        stubs: ['router-link'],
        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    vm.banks.setList([])
    vm.banks.fetching = false
    vm.banks.ready = true
    vm.balance.makeReady({
      available: '0.00',
      escrow: '0.00',
      pending: '0.00',
    })
    vm.willIncurFee.makeReady({value: false})
    await flushPromises()
    mockAxios.reset()
    expect(wrapper.find('.add-account').props('disabled')).toBe(false)
    wrapper.find('.add-account').trigger('click')
    await vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    mockAxios.mockResponse(rs({id: 2, last_four: '1234', type: 0}))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.banks.list.length).toBe(1)
    expect(vm.banks.list[0].x.last_four).toBe('1234')
  })
  it('Prevents addition when the user will incur a fee and has insufficient balance.', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcBankToggleAuthorize, {
        localVue,
        store,
        vuetify,
        propsData: {username: 'Fox', value: 1, manageBanks: true},
        stubs: ['router-link'],
        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    vm.banks.setList([])
    vm.banks.fetching = false
    vm.banks.ready = true
    vm.balance.makeReady({
      available: '0.00',
      escrow: '0.00',
      pending: '0.00',
    })
    vm.willIncurFee.makeReady({value: true})
    await flushPromises()
    mockAxios.reset()
    expect(wrapper.find('.add-account').props('disabled')).toBe(true)
  })
})
