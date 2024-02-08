import {cleanUp, confirmAction, mount, rs, vueSetup, VuetifyWrapped} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import OrderList from '@/components/views/orders/OrderList.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {genArtistProfile, genOrder, genProduct} from '@/specs/helpers/fixtures.ts'
import {afterEach, describe, expect, test} from 'vitest'

let wrapper: VueWrapper<any>

const WrappedOrderList = VuetifyWrapped(OrderList)

describe('OrderList.vue', () => {
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Recognizes when it is on the waiting list page.', async() => {
    wrapper = mount(OrderList, {
      ...vueSetup({
        stubs: ['router-link'],
        mocks: {$route: {query: {}}},
      }),
      props: {
        type: 'sales',
        category: 'waiting',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    expect(vm.salesWaiting).toBe(true)
    await wrapper.setProps({category: 'current'})
    await vm.$nextTick()
    expect(vm.salesWaiting).toBe(false)
    await wrapper.setProps({category: 'orders'})
    await vm.$nextTick()
    expect(vm.salesWaiting).toBe(false)
  })
  test('Loads state from query', async() => {
    wrapper = mount(OrderList, {
      ...vueSetup({
        stubs: ['router-link'],
        mocks: {
          $route: {
            query: {
              q: 'lol',
              product: 10,
            },
          },
        },
      }),
      props: {
        type: 'sales',
        category: 'waiting',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    expect(vm.showProduct).toBe(false)
    expect(vm.productInitItems.length).toBe(0)
    const request = mockAxios.getReqByUrl('/api/sales/account/Fox/products/10/')
    expect(request.method).toBe('get')
    mockAxios.mockResponse(rs(genProduct({
      id: 10,
      name: 'stuff',
    })), request)
    await vm.$nextTick()
    expect(vm.showProduct).toBe(true)
    expect(vm.productInitItems.length).toBe(1)
    expect(vm.productInitItems[0].name).toBe('stuff')
  })
  test('Clears a waitlist', async() => {
    wrapper = mount(WrappedOrderList, {
      ...vueSetup({
        stubs: ['router-link'],
        mocks: {$route: {query: {}}},
      }),
      props: {
        type: 'sales',
        category: 'waiting',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile())
    vm.list.setList([])
    vm.list.ready = true
    vm.list.fetching = false
    await vm.$nextTick()
    vm.searchForm.fields.product.update(100)
    await vm.$nextTick()
    await confirmAction(wrapper, ['.clear-waitlist'])
    await vm.$nextTick()
    const request = mockAxios.getReqByUrl('/api/sales/account/Fox/products/100/clear-waitlist/')
    mockAxios.mockResponse(rs(undefined), request)
    await vm.$nextTick()
    expect(vm.list.ready).toBe(false)
  })
  test('Displays orders in a tabulated manner', async() => {
    wrapper = mount(OrderList, {
      ...vueSetup({
        stubs: ['router-link'],
        mocks: {$route: {query: {}}},
      }),
      props: {
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
        genOrder({
          id: 2,
          read: false,
        }),
        genOrder({
          id: 3,
          buyer: null,
        }),
      ],
    )
    vm.list.ready = true
    vm.list.fetching = false
    vm.dataMode = true
    await vm.$nextTick()
  })
})
