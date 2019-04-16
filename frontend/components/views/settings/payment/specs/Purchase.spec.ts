import Vue from 'vue'
import {cleanUp, flushPromises, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {singleRegistry} from '@/store/singles/registry'
import {listRegistry} from '@/store/lists/registry'
import {profileRegistry} from '@/store/profiles/registry'
import {mount, Wrapper} from '@vue/test-utils'
import {genCard, genUser} from '@/specs/helpers/fixtures'
import Purchase from '@/components/views/settings/payment/Purchase.vue'
import mockAxios from '@/__mocks__/axios';
import {flush} from '@sentry/browser'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

function emptyForm() {
  return {
    card_id: 1,
    country: 'US',
    cvv: '',
    exp_date: '',
    first_name: '',
    last_name: '',
    make_primary: true,
    number: '',
    save_card: true,
    zip: '',
  }
}

describe('Purchase.vue', () => {
  beforeEach(() => {
    store = createStore()
    singleRegistry.reset()
    listRegistry.reset()
    profileRegistry.reset()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Purchase, {
      localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true,
    })
  })
  it('Updates the endpoints when the username is changed', async() => {
    setViewer(store, genUser())
    wrapper = mount(Purchase, {
      localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true,
    })
    const vm = wrapper.vm as any
    expect(vm.cards.endpoint).toBe('/api/sales/v1/account/Fox/cards/')
    wrapper.setProps({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    expect(vm.cards.endpoint).toBe('/api/sales/v1/account/Vulpes/cards/')
  })
  it('Replaces the primary card with a new one', async() => {
    const user = genUser()
    user.landscape = true
    setViewer(store, user)
    wrapper = mount(Purchase, {
      localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true,
    })
    const vm = wrapper.vm as any
    vm.cards.setList([genCard({id: 1, primary: true}), genCard({id: 2}), genCard({id: 4})])
    vm.cards.fetching = false
    vm.cards.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.add-card-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/api/sales/v1/account/Fox/cards/', 'post', emptyForm(), {}))
    const card = genCard({id: 5, primary: true})
    mockAxios.mockResponse(rs(card))
    await flushPromises()
    expect(vm.cards.list.length).toBe(4)
    const output = vm.cards.list[vm.cards.list.length - 1].x
    expect(output.id).toBe(5)
    expect(output.primary).toBe(true)
  })
  it('Replaces the primary card with a new one', async() => {
    const user = genUser()
    user.landscape = true
    setViewer(store, user)
    wrapper = mount(Purchase, {
      localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true,
    })
    const vm = wrapper.vm as any
    vm.cards.setList([genCard({id: 1, primary: true}), genCard({id: 2}), genCard({id: 4})])
    vm.cards.fetching = false
    vm.cards.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.add-card-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/api/sales/v1/account/Fox/cards/', 'post', emptyForm(), {}))
    const card = genCard({id: 5, primary: true})
    mockAxios.mockResponse(rs(card))
    await flushPromises()
    expect(vm.cards.list.length).toBe(4)
    const output = vm.cards.list[vm.cards.list.length - 1].x
    expect(output.id).toBe(5)
    expect(output.primary).toBe(true)
    const oldPrimary = vm.cards.list[0].x
    expect(oldPrimary.primary).toBe(false)
  })
  it('Does not mess with the existing primary when there is not a new one.', async() => {
    const user = genUser()
    user.landscape = true
    setViewer(store, user)
    wrapper = mount(Purchase, {
      localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true,
    })
    const vm = wrapper.vm as any
    vm.cards.setList([genCard({id: 1, primary: true}), genCard({id: 2}), genCard({id: 4})])
    vm.cards.fetching = false
    vm.cards.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.add-card-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/api/sales/v1/account/Fox/cards/', 'post', emptyForm(), {}))
    const card = genCard({id: 5})
    mockAxios.mockResponse(rs(card))
    await flushPromises()
    expect(vm.cards.list.length).toBe(4)
    const output = vm.cards.list[vm.cards.list.length - 1].x
    expect(output.id).toBe(5)
    expect(output.primary).toBe(false)
    const oldPrimary = vm.cards.list[0].x
    expect(oldPrimary.primary).toBe(true)
    expect(oldPrimary.id).toBe(1)
  })
})
