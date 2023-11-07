import {genDeliverable, genInvoice, genUser} from '@/specs/helpers/fixtures'
import {mount, setPricing, setViewer, vueSetup} from '@/specs/helpers'
import {dummyLineItems} from '@/lib/specs/helpers'
import mockAxios from '@/__mocks__/axios'
import {LineTypes} from '@/types/LineTypes'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import {Router} from 'vue-router'
import {deliverableRouter} from '@/components/views/order/specs/helpers'
import MockDate from 'mockdate'
import {parseISO} from '@/lib/lib'
import Empty from '@/specs/helpers/dummy_components/empty'
import {ConnectionStatus} from '@/types/ConnectionStatus'
import AcTippingPrompt from '@/components/views/order/deliverable/AcTippingPrompt.vue'
import {InvoiceStatus} from '@/types/InvoiceStatus'
import {beforeEach, describe, expect, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let empty: VueWrapper<any>

const tipLines = () => {
  return [
    {
      id: 21,
      priority: 300,
      percentage: 4,
      amount: 0.5,
      frozen_value: null,
      type: LineTypes.PROCESSING,
      destination_account: null,
      destination_user: null,
      description: '',
      cascade_percentage: true,
      cascade_amount: true,
      back_into_percentage: false,
    },
    {
      id: 22,
      priority: 300,
      percentage: 4,
      amount: 0.5,
      frozen_value: null,
      type: LineTypes.TIP,
      destination_account: 304,
      destination_user: null,
      description: '',
      cascade_percentage: true,
      cascade_amount: true,
      back_into_percentage: false,
    },
  ]
}

describe('AcTippingPrompt', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
    // This is a saturday.
    MockDate.set(parseISO('2020-08-01'))
    empty = mount(Empty, vueSetup({store}))
    empty.vm.$getSingle('socketState', {
      endpoint: '#',
      persist: true,
      x: {
        status: ConnectionStatus.CONNECTING,
        version: 'beep',
        serverVersion: '',
      },
    })
    setPricing(store)
  })
  test('Permits tipping', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/')
    const deliverableController = empty.vm.$getSingle('deliverable', {endpoint: '#'})
    const deliverable = genDeliverable()
    deliverableController.makeReady(deliverable)
    const sourceLinesController = empty.vm.$getList('lines', {endpoint: '#'})
    sourceLinesController.makeReady(dummyLineItems())
    wrapper = mount(
      AcTippingPrompt, {
        ...vueSetup({
          store,
          stubs: ['ac-revision-manager', 'ac-comment-section'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
          isBuyer: true,
          deliverable,
          sourceLines: sourceLinesController,
          invoiceId: 'abcd',
        },
      })
    const vm = wrapper.vm as any
    const invoice = genInvoice({
      status: InvoiceStatus.DRAFT,
      id: 'abcd',
    })
    const lines = tipLines()
    vm.invoice.makeReady(invoice)
    vm.lineItems.makeReady(lines)
    mockAxios.reset()
    await vm.$nextTick()
    await wrapper.find('.preset10').trigger('click')
    await vm.$nextTick()
    expect(vm.tip.patchers.amount.model).toEqual(8)
  })
  test('Updates an existing tip line item', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5')
    const deliverableController = empty.vm.$getSingle('deliverable', {endpoint: '#'})
    const deliverable = genDeliverable()
    deliverableController.makeReady(deliverable)
    const sourceLinesController = empty.vm.$getList('lines', {endpoint: '#'})
    sourceLinesController.makeReady(dummyLineItems())
    wrapper = mount(
      AcTippingPrompt, {
        ...vueSetup({
          store,
          stubs: ['ac-revision-manager', 'ac-comment-section'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
          isBuyer: true,
          deliverable,
          sourceLines: sourceLinesController,
          invoiceId: 'abcd',
        },
      })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    const lines = tipLines()
    const invoice = genInvoice({
      status: InvoiceStatus.DRAFT,
      id: 'abcd',
    })
    vm.invoice.makeReady(invoice)
    vm.lineItems.makeReady(lines)
    mockAxios.reset()
    vm.setTip(0.25)
    await vm.$nextTick()
    expect(vm.tip.patchers.amount.model).toEqual(20)
  })
})
