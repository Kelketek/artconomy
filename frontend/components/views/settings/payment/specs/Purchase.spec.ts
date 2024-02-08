import {cleanUp, createVuetify, docTarget, flushPromises, mount, rq, rs, setViewer, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {genCard, genUser} from '@/specs/helpers/fixtures.ts'
import Purchase from '@/components/views/settings/payment/Purchase.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {PROCESSORS} from '@/types/PROCESSORS.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

vi.useFakeTimers()

function emptyForm() {
  return {
    card_id: 1,
    make_primary: true,
    save_card: true,
    use_reader: false,
  }
}

describe('Purchase.vue Authorize', () => {
  beforeEach(() => {
    store = createStore()
    window.DEFAULT_CARD_PROCESSOR = PROCESSORS.AUTHORIZE
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
  test('Does not mess with the existing primary when there is not a new one.', async() => {
    const user = genUser()
    user.landscape = true
    setViewer(store, user)
    wrapper = mount(Purchase, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
      attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    const cards = [genCard({
      id: 1,
      primary: true,
    }), genCard({id: 2}), genCard({id: 4})]
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
    await wrapper.find('.add-card-button').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/sales/account/Fox/cards/', 'post', emptyForm(), {}))
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
    store = createStore()
    window.DEFAULT_CARD_PROCESSOR = PROCESSORS.STRIPE
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Sends a new card to Stripe', async() => {
    const user = genUser({username: 'Fox'})
    user.landscape = true
    setViewer(store, user)
    wrapper = mount(Purchase, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    const cards = [genCard({
      id: 1,
      primary: true,
    }), genCard({id: 2}), genCard({id: 4})]
    vm.cards.makeReady(cards)
    vm.clientSecret.makeReady({secret: 'secret'})
    await vm.$nextTick()
    vm.$refs.cardManager.cards.makeReady(cards)
    mockAxios.reset()
    const mockSubmit = vi.spyOn(vm.$refs.cardManager, 'stripeSubmit')
    await wrapper.find('.add-card-button').trigger('click')
    expect(mockSubmit).toHaveBeenCalled()
  })
})
