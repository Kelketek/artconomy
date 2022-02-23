import Vue from 'vue'
import {Wrapper} from '@vue/test-utils'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {cleanUp, createVuetify, docTarget, flushPromises, mount, rq, rs, vueSetup} from '@/specs/helpers'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import mockAxios from '@/__mocks__/axios'
import {PROCESSORS} from '@/types/PROCESSORS'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let generator: Wrapper<Vue>
let cardList: ListController<CreditCardToken>
let vuetify: Vuetify

describe('AcCard.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    generator = mount(Empty, {localVue, store})
    cardList = generator.vm.$getList('creditCards', {endpoint: '/cards/'})
    cardList.setList([{id: 1, last_four: '1234', primary: true, type: 1, cvv_verified: true, processor: PROCESSORS.AUTHORIZE}])
    wrapper = mount(
      AcCard, {
        localVue, store, vuetify, attachTo: docTarget(), propsData: {cardList, card: cardList.list[0]},
      })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts and displays a card', () => {
    expect(wrapper.find('.fa-cc-visa').exists()).toBe(true)
    expect(wrapper.find('.default-indicator').exists()).toBe(true)
  })
  it('Deletes a card', async() => {
    const mockGet = jest.spyOn(cardList, 'get')
    wrapper.find('.delete-card').trigger('click')
    // Confirmation.
    await wrapper.vm.$nextTick()
    wrapper.find('.delete-confirm .confirmation-button').trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/cards/1/', 'delete'))
    mockAxios.mockResponse({status: 204, data: {}})
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(mockGet).toHaveBeenCalled()
  })
  it('Marks a card as primary', async() => {
    cardList.list[0].updateX({primary: false})
    cardList.push({id: 2, cvv_verified: true, last_four: '5432', primary: true, type: 2, processor: PROCESSORS.AUTHORIZE})
    cardList.push({id: 3, cvv_verified: true, last_four: '4563', primary: false, type: 3, processor: PROCESSORS.AUTHORIZE})
    cardList.list[2].setX(null)
    await wrapper.vm.$nextTick()
    wrapper.find('.make-default').trigger('click')
    // Confirmation.
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/cards/1/primary/', 'post', undefined, {}))
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    expect((cardList.list[0].x as CreditCardToken).primary).toBe(true)
    expect((cardList.list[1].x as CreditCardToken).primary).toBe(false)
  })
  it('Shows the correct icon for a card', async() => {
    const vm = wrapper.vm as any
    vm.card.updateX({type: 1})
    await vm.$nextTick()
    expect(wrapper.find('.fa-cc-visa').exists()).toBe(true)
    vm.card.updateX({type: 2})
    await vm.$nextTick()
    expect(wrapper.find('.fa-cc-mastercard').exists()).toBe(true)
    vm.card.setX(null)
    await vm.$nextTick()
    // This will never actually be displayed, because a non-existent card shouldn't be rendered.
    expect(wrapper.find('.fa-credit-card-alt').exists()).toBe(false)
    expect(vm.cardIcon).toBe('fa-credit-card-alt')
  })
})
