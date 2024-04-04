import {VueWrapper} from '@vue/test-utils'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'

import {ArtStore, createStore} from '@/store/index.ts'
import {
  cleanUp,
  createTestRouter,
  createVuetify,
  docTarget,
  flushPromises,
  mount,
  rq,
  rs,
  vueSetup,
} from '@/specs/helpers/index.ts'
import {ListController} from '@/store/lists/controller.ts'
import {CreditCardToken} from '@/types/CreditCardToken.ts'
import mockAxios from '@/__mocks__/axios.ts'
import {genCard, genUser} from '@/specs/helpers/fixtures.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {baseCardSchema, setViewer} from '@/lib/lib.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {nextTick} from 'vue'
import {getStripe} from '@/components/views/order/mixins/StripeMixin.ts'

let store: ArtStore
let wrapper: VueWrapper<any>
let vm: any
let ccForm: FormController
let cards: ListController<CreditCardToken>

describe('AcCardManager.vue Stripe', () => {
  beforeEach(() => {
    store = createStore()
    setViewer(store, genUser())
    ccForm = mount(Empty, vueSetup({store})).vm.$getForm('newCard', baseCardSchema('/test/'))
    const router = createTestRouter()
    wrapper = mount(
      AcCardManager, {
        ...vueSetup({store, router}),
        props: {
          username: 'Fox',
          clientSecret: 'Beep',
          ccForm,
        },
      })
    vm = wrapper.vm
    // @ts-expect-error
    getStripe()!.setupValue = {}
    cards = (wrapper.vm as any).cards
  })
  test('Fetches the initial data', async() => {
    expect(mockAxios.request.mock.calls[1][0]).toEqual(
      rq('/api/sales/account/Fox/cards/', 'get', undefined, {signal: expect.any(Object)}),
    )
  })
  test('Updates the endpoint when the username is changed', async() => {
    const vm = wrapper.vm as any
    expect(vm.cards.endpoint).toBe('/api/sales/account/Fox/cards/')
    await wrapper.setProps({username: 'Vulpes'})
    await nextTick()
    expect(vm.cards.endpoint).toBe('/api/sales/account/Vulpes/cards/')
  })
  test('Switches tabs depending on whether cards are present', async() => {
    const vm = wrapper.vm as any
    expect(vm.cards.endpoint).toBe('/api/sales/account/Fox/cards/')
    await wrapper.setProps({username: 'Vulpes'})
    await nextTick()
    expect(vm.cards.endpoint).toBe('/api/sales/account/Vulpes/cards/')
    vm.cards.setList([genCard()])
    await nextTick()
    expect(vm.tab).toBe('saved-cards')
    vm.cards.setList([])
    await nextTick()
    expect(vm.tab).toBe('new-card')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Fetches the initial data', async() => {
    expect(mockAxios.request.mock.calls[1][0]).toEqual(
      rq('/api/sales/account/Fox/cards/', 'get', undefined, {signal: expect.any(Object)}),
    )
  })
  test('Handles cleanup after saving a card', async() => {
    await wrapper.setProps({
      saveOnly: true,
      clientSecret: 'Beep',
    })
    vm.tab = 'new-card'
    // @ts-expect-error
    getStripe()!.setupValue = {}
    await vm.$nextTick()
    expect(ccForm.errors).toEqual([])
    vm.stripeSubmit()
    await flushPromises()
    await vm.$nextTick()
    expect(ccForm.errors).toEqual([])
    expect(vm.tab).toBe('saved-cards')
  })
  test('Handles a stripe error when saving a card', async() => {
    await wrapper.setProps({
      saveOnly: true,
      clientSecret: 'Beep',
    })
    vm.tab = 'new-card'
    // @ts-expect-error
    getStripe()!.setupValue = {
      error: {
        code: 'Failure',
        message: 'Shit broke.',
      },
    }
    await vm.$nextTick()
    expect(ccForm.errors).toEqual([])
    vm.stripeSubmit()
    await flushPromises()
    await vm.$nextTick()
    expect(ccForm.errors).toEqual(['Shit broke.'])
    expect(vm.tab).toBe('new-card')
  })
})
