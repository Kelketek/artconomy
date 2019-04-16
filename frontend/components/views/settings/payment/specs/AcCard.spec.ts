import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import Vuetify from 'vuetify'
import {ArtStore, createStore} from '@/store'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {listRegistry, Lists} from '@/store/lists/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {flushPromises, rq, rs, vuetifySetup} from '@/specs/helpers'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import mockAxios from '@/__mocks__/axios'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)
let store: ArtStore
let wrapper: Wrapper<Vue>
let generator: Wrapper<Vue>
let cardList: ListController<CreditCardToken>

describe('ac-card', () => {
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    listRegistry.reset()
    profileRegistry.reset()
    mockAxios.reset()
    generator = mount(Empty, {localVue, store})
    cardList = generator.vm.$getList('creditCards', {endpoint: '/cards/'})
    cardList.setList([{id: 1, last_four: '1234', primary: true, type: 1, cvv_verified: true}])
    wrapper = mount(
      AcCard, {
        localVue, store, sync: false, attachToDocument: true, propsData: {cardList, card: cardList.list[0]},
      })
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
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
    expect(mockAxios.delete).toHaveBeenCalledWith(...rq('/cards/1/', 'delete'))
    mockAxios.mockResponse({status: 204, data: {}})
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(mockGet).toHaveBeenCalled()
  })
  it('Marks a card as primary', async() => {
    cardList.list[0].updateX({primary: false})
    cardList.push({id: 2, cvv_verified: true, last_four: '5432', primary: true, type: 2})
    cardList.push({id: 3, cvv_verified: true, last_four: '4563', primary: false, type: 3})
    cardList.list[2].setX(false)
    await wrapper.vm.$nextTick()
    wrapper.find('.make-default').trigger('click')
    // Confirmation.
    expect(mockAxios.post).toHaveBeenCalledWith(...rq('/cards/1/primary/', 'post', undefined, {}))
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    expect((cardList.list[0].x as CreditCardToken).primary).toBe(true)
    expect((cardList.list[1].x as CreditCardToken).primary).toBe(false)
  })
})
