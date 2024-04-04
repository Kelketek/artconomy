import {
  cleanUp,
  createTestRouter,
  mount,
  vueSetup,
  waitFor,
} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {genCard, genUser} from '@/specs/helpers/fixtures.ts'
import Purchase from '@/components/views/settings/payment/Purchase.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import {Router} from 'vue-router'

let store: ArtStore
let wrapper: VueWrapper<any>

vi.useFakeTimers()

describe('Purchase.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Purchase, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
  })
  test('Updates the endpoints when the username is changed', async() => {
    setViewer(store, genUser())
    wrapper = mount(Purchase, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    expect(vm.cards.endpoint).toBe('/api/sales/account/Fox/cards/')
    wrapper.setProps({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    expect(vm.cards.endpoint).toBe('/api/sales/account/Vulpes/cards/')
  })
  test('Sends a new card to Stripe', async() => {
    const user = genUser({username: 'Fox'})
    user.landscape = true
    setViewer(store, user)
    wrapper = mount(Purchase, {
      ...vueSetup({store}),
      props: {username: 'Fox', saveOnly: true},
    })
    const vm = wrapper.vm as any
    const cards = [genCard({
      id: 1,
      primary: true,
    }), genCard({id: 2}), genCard({id: 4})]
    vm.cards.makeReady(cards)
    vm.clientSecret.makeReady({secret: 'secret'})
    await waitFor(() => expect((wrapper.findComponent(AcCardManager).vm as any).stripeSubmit).toBeTruthy())
    const cardManager = wrapper.findComponent(AcCardManager).vm as any
    cardManager.cards.makeReady(cards)
    mockAxios.reset()
    const mockSubmit = vi.fn()
    Object.defineProperty(cardManager, 'stripeSubmit', {value: mockSubmit})
    cardManager.stripeSubmit = mockSubmit
    await wrapper.find('.add-card-button').trigger('click')
    expect(window.Stripe!('beep').confirmCardSetup).toHaveBeenCalled()
  })
})
