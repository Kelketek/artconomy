import {createVuetify, mount, vueSetup} from '@/specs/helpers'
import AcSavedCardField from '@/components/fields/AcSavedCardField.vue'
import {ArtStore, createStore} from '@/store'
import Empty from '@/specs/helpers/dummy_components/empty'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import {genCard} from '@/specs/helpers/fixtures'
import {describe, expect, beforeEach, test, vi} from 'vitest'

let store: ArtStore
let cards: ListController<CreditCardToken>

describe('AcSavedCardField.vue', () => {
  beforeEach(() => {
    store = createStore()
    cards = mount(Empty, vueSetup({store})).vm.$getList('cards', {endpoint: '/cards/'})
    const cardSet = [genCard(), genCard(), genCard()]
    cardSet[1].id = 2
    cardSet[2].id = 3
    cards.setList(cardSet)
    cards.ready = true
    cards.fetching = false
  })
  test('Sends the right information', async() => {
    mount(Empty, vueSetup({store}))
    const wrapper = mount(AcSavedCardField, {
      ...vueSetup({store}),
      props: {
        cards,
        modelValue: 1,
      },
    })
    await wrapper.findAll('input').at(1)!.trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([2])
  })
})
