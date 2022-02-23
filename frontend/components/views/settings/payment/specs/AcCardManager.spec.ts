import Vue from 'vue'
import {Wrapper} from '@vue/test-utils'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, flushPromises, rq, rs, setViewer, vueSetup, mount} from '@/specs/helpers'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import mockAxios from '@/__mocks__/axios'
import {genCard, genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {baseCardSchema} from '@/lib/lib'
import {PROCESSORS} from '@/types/PROCESSORS'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let cards: ListController<CreditCardToken>
let vuetify: Vuetify

function genList() {
  return [
    {id: 1, last_four: '1234', primary: true, type: 1, cvv_verified: true},
    {id: 2, last_four: '5432', primary: false, type: 2, cvv_verified: true},
    {id: 3, last_four: '4563', primary: false, type: 3, cvv_verified: true},
  ]
}

describe('AcCardManager.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    setViewer(store, genUser())
    const ccForm = mount(Empty, {localVue, store}).vm.$getForm('newCard', baseCardSchema('/test/'))
    wrapper = mount(
      AcCardManager, {
        localVue,
        store,
        vuetify,
        attachTo: docTarget(),
        propsData: {username: 'Fox', ccForm, processor: PROCESSORS.AUTHORIZE},
      })
    cards = (wrapper.vm as any).cards
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Fetches the initial data', async() => {
    expect(mockAxios.request.mock.calls[0][0]).toEqual(
      rq('/api/sales/v1/account/Fox/cards/authorize/', 'get', undefined, {cancelToken: expect.any(Object)}),
    )
  })
  it('Updates the endpoint when the username is changed', async() => {
    const vm = wrapper.vm as any
    expect(vm.cards.endpoint).toBe('/api/sales/v1/account/Fox/cards/authorize/')
    wrapper.setProps({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    expect(vm.cards.endpoint).toBe('/api/sales/v1/account/Vulpes/cards/authorize/')
  })
  it('Switches tabs depending on whether cards are present', async() => {
    const vm = wrapper.vm as any
    expect(vm.cards.endpoint).toBe('/api/sales/v1/account/Fox/cards/authorize/')
    wrapper.setProps({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    expect(vm.cards.endpoint).toBe('/api/sales/v1/account/Vulpes/cards/authorize/')
    vm.cards.setList([genCard()])
    await wrapper.vm.$nextTick()
    expect(vm.tab).toBe('saved-cards')
    vm.cards.setList([])
    await wrapper.vm.$nextTick()
    expect(vm.tab).toBe('new-card')
  })
  it('Saves the last valid card ID', async() => {
    const vm = wrapper.vm as any
    expect(vm.cards.endpoint).toBe('/api/sales/v1/account/Fox/cards/authorize/')
    wrapper.setProps({value: 3})
    await wrapper.vm.$nextTick()
    expect(vm.lastCard).toBe(3)
    wrapper.setProps({value: null})
    await wrapper.vm.$nextTick()
    expect(vm.lastCard).toBe(3)
  })
  it('Reveals the CVV field when the card id is set and the card is not verified', async() => {
    const cardList = genList()
    cardList[0].cvv_verified = false
    wrapper.setProps({value: 1})
    mockAxios.mockResponse(rs(cardList))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.cvv-verify').exists()).toBe(true)
  })
  it('Generates a useful URL when no particular processor is selected', async() => {
    const cardList = genList()
    cardList[0].cvv_verified = false
    wrapper.setProps({processor: undefined})
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.url).toBe('/api/sales/v1/account/Fox/cards/')
  })
})
