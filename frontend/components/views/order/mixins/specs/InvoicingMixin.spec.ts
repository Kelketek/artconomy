import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import DummyInvoice from '@/specs/helpers/dummy_components/DummyInvoice.vue'
import Empty from '@/specs/helpers/dummy_components/empty'
import {ListController} from '@/store/lists/controller'
import LineItem from '@/types/LineItem'
import {genDeliverable, genOrder, genProduct} from '@/specs/helpers/fixtures'
import {VueWrapper} from '@vue/test-utils'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let store: ArtStore
let invoiceLineItems: ListController<LineItem>
let wrapper: VueWrapper<any>

describe('InvoicingMixin.ts', () => {
  beforeEach(() => {
    store = createStore()
    const empty = mount(Empty, vueSetup({store})).vm
    invoiceLineItems = empty.$getList('lineItems', {endpoint: '/test/'})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Updates the task weight', async() => {
    wrapper = mount(DummyInvoice, {
      ...vueSetup({store}),
      props: {
        invoiceEscrowEnabled: true,
        invoiceLineItems,
        username: 'Fox',
        showBuyer: true,
      },
    })
    const vm = wrapper.vm as any
    await wrapper.vm.$nextTick()
    expect(vm.newInvoice.fields.task_weight.value).toBe(0)
    vm.invoiceProduct.setX(genProduct({task_weight: 3}))
    await vm.$nextTick()
    expect(vm.newInvoice.fields.task_weight.value).toBe(3)
  })
  test('Refetches the product when a new value is set', async() => {
    wrapper = mount(DummyInvoice, {
      ...vueSetup({store}),
      props: {
        invoiceEscrowEnabled: true,
        invoiceLineItems,
        username: 'Fox',
        showBuyer: true,
      },
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    vm.invoiceProduct.setX(genProduct({id: 1}))
    await vm.$nextTick()
    const mockKill = vi.spyOn(vm.invoiceProduct, 'kill')
    const mockGet = vi.spyOn(vm.invoiceProduct, 'get')
    vm.newInvoice.fields.product.update(255)
    await vm.$nextTick()
    expect(mockKill).toHaveBeenCalled()
    expect(mockGet).toHaveBeenCalled()
    expect(vm.invoiceProduct.endpoint).toBe('/api/sales/account/Fox/products/255/')
  })
  test('Goes to the new deliverable', async() => {
    const push = vi.fn()
    wrapper = mount(DummyInvoice, {
      ...vueSetup({
        store,
        mocks: {$router: {push}},
      }),
      props: {
        invoiceEscrowEnabled: true,
        invoiceLineItems,
        username: 'Fox',
        showBuyer: true,
      },
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    vm.goToOrder(genDeliverable({
      id: 120,
      order: genOrder({id: 100}),
    }))
    expect(push).toHaveBeenCalledWith(
      {
        name: 'SaleDeliverableOverview',
        params: {
          deliverableId: '120',
          orderId: '100',
          username: 'Fox',
        },
      })
  })
})
