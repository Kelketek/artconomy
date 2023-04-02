import Vue from 'vue'
import {cleanUp, qMount, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import DummyInvoice from '@/specs/helpers/dummy_components/DummyInvoice.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ListController} from '@/store/lists/controller'
import LineItem from '@/types/LineItem'
import {genDeliverable, genOrder, genProduct} from '@/specs/helpers/fixtures'
import {Wrapper} from '@vue/test-utils'

const localVue = vueSetup()
let store: ArtStore
let invoiceLineItems: ListController<LineItem>
let wrapper: Wrapper<Vue>

describe('InvoicingMixin.ts', () => {
  beforeEach(() => {
    store = createStore()
    const empty = qMount(Empty, {localVue, store, attachTo: ''}).vm
    invoiceLineItems = empty.$getList('lineItems', {endpoint: '/test/'})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Updates the task weight', async() => {
    wrapper = qMount(DummyInvoice, {
      localVue,
      store,
      propsData: {
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
  it('Refetches the product when a new value is set', async() => {
    wrapper = qMount(DummyInvoice, {
      localVue,
      store,
      propsData: {
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
    const mockKill = jest.spyOn(vm.invoiceProduct, 'kill')
    const mockGet = jest.spyOn(vm.invoiceProduct, 'get')
    vm.newInvoice.fields.product.update(255)
    await vm.$nextTick()
    expect(mockKill).toHaveBeenCalled()
    expect(mockGet).toHaveBeenCalled()
    expect(vm.invoiceProduct.endpoint).toBe('/api/sales/v1/account/Fox/products/255/')
  })
  it('Goes to the new deliverable', async() => {
    const push = jest.fn()
    wrapper = qMount(DummyInvoice, {
      localVue,
      store,
      mocks: {$router: {push}},
      propsData: {
        invoiceEscrowEnabled: true,
        invoiceLineItems,
        username: 'Fox',
        showBuyer: true,
      },
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    vm.goToOrder(genDeliverable({id: 120, order: genOrder({id: 100})}))
    expect(push).toHaveBeenCalledWith(
      {name: 'SaleDeliverableOverview', params: {deliverableId: '120', orderId: '100', username: 'Fox'}})
  })
})
