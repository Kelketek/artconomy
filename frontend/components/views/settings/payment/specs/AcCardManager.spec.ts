import {VueWrapper} from '@vue/test-utils'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'

import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, flushPromises, mount, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import mockAxios from '@/__mocks__/axios'
import {genCard, genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty'
import {baseCardSchema} from '@/lib/lib'
import {PROCESSORS} from '@/types/PROCESSORS'
import {FormController} from '@/store/forms/form-controller'
import {genPricing} from '@/lib/specs/helpers'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let vm: any
let ccForm: FormController
let cards: ListController<CreditCardToken>

function genList() {
  return [
    {
      id: 1,
      last_four: '1234',
      primary: true,
      type: 1,
      cvv_verified: true,
    },
    {
      id: 2,
      last_four: '5432',
      primary: false,
      type: 2,
      cvv_verified: true,
    },
    {
      id: 3,
      last_four: '4563',
      primary: false,
      type: 3,
      cvv_verified: true,
    },
  ]
}

describe('AcCardManager.vue Authorize', () => {
  beforeEach(() => {
    store = createStore()
    setViewer(store, genUser())
    const ccForm = mount(Empty, vueSetup({store})).vm.$getForm('newCard', baseCardSchema('/test/'))
    wrapper = mount(
      AcCardManager, {
        ...vueSetup({store}),
        props: {
          username: 'Fox',
          ccForm,
          processor: PROCESSORS.AUTHORIZE,
        },
      })
    cards = (wrapper.vm as any).cards
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Fetches the initial data', async() => {
    expect(mockAxios.request.mock.calls[1][0]).toEqual(
      rq('/api/sales/account/Fox/cards/authorize/', 'get', undefined, {signal: expect.any(Object)}),
    )
  })
  test('Updates the endpoint when the username is changed', async() => {
    const vm = wrapper.vm as any
    expect(vm.cards.endpoint).toBe('/api/sales/account/Fox/cards/authorize/')
    await wrapper.setProps({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    expect(vm.cards.endpoint).toBe('/api/sales/account/Vulpes/cards/authorize/')
  })
  test('Switches tabs depending on whether cards are present', async() => {
    const vm = wrapper.vm as any
    expect(vm.cards.endpoint).toBe('/api/sales/account/Fox/cards/authorize/')
    await wrapper.setProps({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    expect(vm.cards.endpoint).toBe('/api/sales/account/Vulpes/cards/authorize/')
    vm.cards.setList([genCard()])
    await wrapper.vm.$nextTick()
    expect(vm.tab).toBe('saved-cards')
    vm.cards.setList([])
    await wrapper.vm.$nextTick()
    expect(vm.tab).toBe('new-card')
  })
})

describe('AcCardManager.vue Stripe', () => {
  beforeEach(() => {
    store = createStore()
    setViewer(store, genUser())
    ccForm = mount(Empty, vueSetup({store})).vm.$getForm('newCard', baseCardSchema('/test/'))
    wrapper = mount(
      AcCardManager, {
        ...vueSetup({store}),
        props: {
          username: 'Fox',
          ccForm,
          processor: PROCESSORS.STRIPE,
        },
      })
    vm = wrapper.vm
    vm.stripe().setupValue = {}
    cards = (wrapper.vm as any).cards
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Fetches the initial data', async() => {
    expect(mockAxios.request.mock.calls[1][0]).toEqual(
      rq('/api/sales/account/Fox/cards/stripe/', 'get', undefined, {signal: expect.any(Object)}),
    )
  })
  test('Handles cleanup after saving a card', async() => {
    await wrapper.setProps({
      saveOnly: true,
      clientSecret: 'Beep',
    })
    vm.tab = 'new-card'
    vm.stripe().setupValue = {}
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
    vm.stripe().setupValue = {
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
