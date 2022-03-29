import Vue from 'vue'
import {cleanUp, createVuetify, docTarget, flushPromises, mount, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import {genCard, genUser} from '@/specs/helpers/fixtures'
import Purchase from '@/components/views/settings/payment/Purchase.vue'
import mockAxios from '@/__mocks__/axios'
import Vuetify from 'vuetify/lib'
import {PROCESSORS} from '@/types/PROCESSORS'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

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
    use_reader: false,
  }
}

describe('Purchase.vue Authorize', () => {
  beforeEach(() => {
    vuetify = createVuetify()
    store = createStore()
    window.DEFAULT_CARD_PROCESSOR = PROCESSORS.AUTHORIZE
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Purchase, {
      localVue, store, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget(),
    })
  })
  it('Updates the endpoints when the username is changed', async() => {
    setViewer(store, genUser())
    wrapper = mount(Purchase, {
      localVue, store, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget(),
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
      localVue, store, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    const cards = [genCard({id: 1, primary: true}), genCard({id: 2}), genCard({id: 4})]
    vm.cards.setList(cards)
    vm.cards.fetching = false
    vm.cards.ready = true
    vm.clientSecret.makeReady({secret: 'secret'})
    await vm.$nextTick()
    vm.$refs.cardManager.cards.setList(cards)
    vm.$refs.cardManager.cards.ready = true
    vm.$refs.cardManager.cards.fetching = false
    await vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.add-card-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/sales/v1/account/Fox/cards/', 'post', emptyForm(), {}))
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
      localVue, store, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    const cards = [genCard({id: 1, primary: true}), genCard({id: 2}), genCard({id: 4})]
    vm.cards.setList(cards)
    vm.cards.fetching = false
    vm.cards.ready = true
    vm.clientSecret.makeReady({secret: 'secret'})
    await vm.$nextTick()
    vm.$refs.cardManager.cards.setList(cards)
    vm.$refs.cardManager.cards.ready = true
    vm.$refs.cardManager.cards.fetching = false
    await vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.add-card-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/sales/v1/account/Fox/cards/', 'post', emptyForm(), {}))
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

describe('Purchase.vue Stripe', () => {
  beforeEach(() => {
    vuetify = createVuetify()
    store = createStore()
    window.DEFAULT_CARD_PROCESSOR = PROCESSORS.STRIPE
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Sends a new card to Stripe', async() => {
    const user = genUser({username: 'Fox'})
    user.landscape = true
    setViewer(store, user)
    wrapper = mount(Purchase, {
      localVue, store, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    const cards = [genCard({id: 1, primary: true}), genCard({id: 2}), genCard({id: 4})]
    vm.cards.makeReady(cards)
    vm.clientSecret.makeReady({secret: 'secret'})
    await vm.$nextTick()
    vm.$refs.cardManager.cards.makeReady(cards)
    mockAxios.reset()
    const mockSubmit = jest.spyOn(vm.$refs.cardManager, 'stripeSubmit')
    wrapper.find('.add-card-button').trigger('click')
    expect(mockSubmit).toHaveBeenCalled()
  })
})
