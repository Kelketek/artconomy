import Vue from 'vue'
import {makeSpace, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {singleRegistry} from '@/store/singles/registry'
import {listRegistry} from '@/store/lists/registry'
import {profileRegistry} from '@/store/profiles/registry'
import {mount, Wrapper} from '@vue/test-utils'
import {genUser} from '@/specs/helpers/fixtures'
import AcBankToggle from '@/components/fields/AcBankToggle.vue'
import mockAxios from '@/__mocks__/axios'
import flushPromises from 'flush-promises'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcBankToggle.vue', () => {
  beforeEach(() => {
    store = createStore()
    singleRegistry.reset()
    listRegistry.reset()
    profileRegistry.reset()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcBankToggle, {
        localVue,
        store,
        propsData: {username: 'Fox', value: 1},
        stubs: ['router-link'],
        sync: false,
        attachToDocument: true,
      })
  })
  it('Changes the bank status setting', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcBankToggle, {
        localVue,
        store,
        propsData: {username: 'Fox', value: 1},
        stubs: ['router-link'],
        sync: false,
        attachToDocument: true,
      })
    const mockEmit = jest.spyOn(wrapper.vm, '$emit')
    wrapper.find('.no-us-account').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockEmit).toHaveBeenCalledWith('input', 2)
  })
  it('Adds a bank', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcBankToggle, {
        localVue,
        store,
        propsData: {username: 'Fox', value: 1, manageBanks: true},
        stubs: ['router-link'],
        sync: false,
        attachToDocument: true,
      })
    const vm = wrapper.vm as any
    vm.banks.setList([])
    vm.banks.fetching = false
    vm.banks.ready = true
    await flushPromises()
    mockAxios.reset()
    wrapper.find('.add-account').trigger('click')
    await vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    mockAxios.mockResponse(rs({id: 2, last_four: '1234', type: 0}))
    await flushPromises()
    await vm.$nextTick()
    expect(wrapper.find('.bank-label').text()).toContain('Checking')
    expect(wrapper.find('.bank-label').text()).toContain('ending in 1234')
  })
})
