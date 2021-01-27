import Vuetify from 'vuetify/lib'
import {createVuetify, vueSetup, mount} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import AcStarField from '@/components/fields/AcStarField.vue'

const localVue = vueSetup()
let store: ArtStore
let cards: ListController<CreditCardToken>
let vuetify: Vuetify

describe('AcSavedCardField.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  it('Sends the right information', async() => {
    mount(Empty)
    const wrapper = mount(AcStarField, {
      localVue,
      store,
      vuetify,
      propsData: {cards, value: null},
    })
    const spyEmit = jest.spyOn(wrapper.vm, '$emit')
    wrapper.findAll('.v-icon').at(2).trigger('click')
    await wrapper.vm.$nextTick()
    expect(spyEmit).toHaveBeenCalledWith('input', 3)
  })
})
