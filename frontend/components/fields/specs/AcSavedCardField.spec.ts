import {vueSetup} from '@/specs/helpers'
import AcSavedCardField from '@/components/fields/AcSavedCardField.vue'
import {mount} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import {genCard} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let store: ArtStore
let cards: ListController<CreditCardToken>

describe('AcSavedCardField.vue', () => {
  beforeEach(() => {
    store = createStore()
    cards = mount(Empty, {localVue, store}).vm.$getList('cards', {endpoint: '/cards/'})
    const cardSet = [genCard(), genCard(), genCard()]
    cardSet[1].id = 2
    cardSet[2].id = 3
    cards.setList(cardSet)
    cards.ready = true
    cards.fetching = false
  })
  it('Sends the right information', async() => {
    mount(Empty)
    const wrapper = mount(AcSavedCardField, {localVue, store, propsData: {cards, value: 1}})
    const spyEmit = jest.spyOn(wrapper.vm, '$emit')
    wrapper.findAll('input').at(1).trigger('click')
    await wrapper.vm.$nextTick()
    expect(spyEmit).toHaveBeenCalledWith('input', 2)
  })
})
