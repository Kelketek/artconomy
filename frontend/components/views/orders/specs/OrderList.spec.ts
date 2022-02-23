import Vue from 'vue'
import {cleanUp, confirmAction, qMount, rs, vueSetup} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import OrderList from '@/components/views/orders/OrderList.vue'
import mockAxios from '@/__mocks__/axios'
import {genArtistProfile, genOrder, genProduct} from '@/specs/helpers/fixtures'

let wrapper: Wrapper<Vue>
const localVue = vueSetup()

describe('OrderList.vue', () => {
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Recognizes when it is on the waiting list page.', async() => {
    wrapper = qMount(OrderList, {
      localVue,
      propsData: {
        type: 'sales',
        category: 'waiting',
        username: 'Fox',
      },
      mocks: {$route: {query: {}}},
    })
    const vm = wrapper.vm as any
    expect(vm.salesWaiting).toBe(true)
    wrapper.setProps({category: 'current'})
    await vm.$nextTick()
    expect(vm.salesWaiting).toBe(false)
    wrapper.setProps({category: 'orders'})
    await vm.$nextTick()
    expect(vm.salesWaiting).toBe(false)
  })
  it('Loads state from query', async() => {
    wrapper = qMount(OrderList, {
      localVue,
      propsData: {
        type: 'sales',
        category: 'waiting',
        username: 'Fox',
      },
      mocks: {$route: {query: {q: 'lol', product: 10}}},
    })
    const vm = wrapper.vm as any
    expect(vm.showProduct).toBe(false)
    expect(vm.productInitItems.length).toBe(0)
    const request = mockAxios.getReqByUrl('/api/sales/v1/account/Fox/products/10/')
    expect(request.method).toBe('get')
    mockAxios.mockResponse(rs(genProduct({id: 10, name: 'stuff'})), request)
    await vm.$nextTick()
    expect(vm.showProduct).toBe(true)
    expect(vm.productInitItems.length).toBe(1)
    expect(vm.productInitItems[0].name).toBe('stuff')
  })
  it('Clears a waitlist', async() => {
    wrapper = qMount(OrderList, {
      localVue,
      propsData: {
        type: 'sales',
        category: 'waiting',
        username: 'Fox',
      },
      mocks: {$route: {query: {}}},
    })
    const vm = wrapper.vm as any
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile())
    vm.list.setList([])
    vm.list.ready = true
    vm.list.fetching = false
    await vm.$nextTick()
    vm.searchForm.fields.product.update(100)
    await vm.$nextTick()
    await confirmAction(wrapper, ['.clear-waitlist'])
    await vm.$nextTick()
    const request = mockAxios.getReqByUrl('/api/sales/v1/account/Fox/products/100/clear-waitlist/')
    mockAxios.mockResponse(rs(undefined), request)
    await vm.$nextTick()
    expect(vm.list.ready).toBe(false)
  })
  it('Displays orders in a tabulated manner', async() => {
    wrapper = qMount(OrderList, {
      localVue,
      propsData: {
        type: 'sales',
        category: 'waiting',
        username: 'Fox',
      },
      mocks: {$route: {query: {}}},
      stubs: ['router-link'],
    })
    const vm = wrapper.vm as any
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile())
    vm.list.setList(
      [
        genOrder({id: 1}),
        genOrder({id: 2, read: false}),
        genOrder({id: 3, buyer: null}),
      ],
    )
    vm.list.ready = true
    vm.list.fetching = false
    vm.dataMode = true
    await vm.$nextTick()
  })
})
