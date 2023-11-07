import {cleanUp, mount, setViewer, vueSetup, VuetifyWrapped} from '@/specs/helpers'
import {createRouter, createWebHistory, Router} from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import Orders from '@/components/views/orders/Orders.vue'
import {genArtistProfile, genCommissionStats, genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty'
import {genPricing} from '@/lib/specs/helpers'
import OrderList from '@/components/views/orders/OrderList.vue'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'
import mockAxios from '@/__mocks__/axios'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let store: ArtStore
let router: Router
let wrapper: VueWrapper<any>

const WrappedOrders = VuetifyWrapped(Orders)

describe('Orders.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [{
        name: 'Sales',
        path: '/sales/:username/',
        props: true,
        component: Empty,
        children: [
          {
            name: 'CurrentSales',
            path: 'current',
            component: OrderList,
            props: true,
          },
          {
            name: 'ArchivedSales',
            path: 'archived',
            component: OrderList,
            props: true,
          },
          {
            name: 'CancelledSales',
            path: 'canceled',
            component: OrderList,
            props: true,
          },
          {
            name: 'WaitingSales',
            path: 'waiting',
            component: OrderList,
            props: true,
          },
        ],
      }, {
        name: 'Orders',
        path: '/orders/:username/',
        props: true,
        component: Empty,
        children: [
          {
            name: 'CurrentOrders',
            path: 'current',
            component: OrderList,
          },
          {
            name: 'ArchivedOrders',
            path: 'archived',
            component: OrderList,
          },
          {
            name: 'CancelledOrders',
            path: 'canceled',
            component: OrderList,
          },
          {
            name: 'WaitingOrders',
            path: 'waiting',
            component: OrderList,
          },
        ],
      }, {
        name: 'BuyAndSell',
        props: true,
        component: Empty,
        path: '/b-n-s/:question',
      }, {
        name: 'Store',
        props: true,
        component: Empty,
        path: '/store/:username',
      }, {
        name: 'Home',
        component: Empty,
        path: '/',
      }],
    })
    vi.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Sets up the order list', async() => {
    setViewer(store, genUser())
    const wrapper = mount(Orders, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Fox',
        seller: true,
        baseName: 'Sales',
      },
    })
    const vm = wrapper.vm as any
    vm.pricing.makeReady(genPricing())
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile({bank_account_status: BANK_STATUSES.IN_SUPPORTED_COUNTRY}))
    await vm.$nextTick()
    expect(vm.closed).toBe(null)
  })
  test('Handles commission stats', async() => {
    setViewer(store, genUser())
    const wrapper = mount(Orders, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Fox',
        seller: true,
        baseName: 'Sales',
      },
    })
    const vm = wrapper.vm as any
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile({bank_account_status: BANK_STATUSES.IN_SUPPORTED_COUNTRY}))
    vm.stats.setX(genCommissionStats())
    await vm.$nextTick()
    expect(vm.closed).toBe(false)
  })
  test('Triggers the invoicing form, and evaluates requisite functions', async() => {
    setViewer(store, genUser())
    const wrapper = mount(WrappedOrders, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Fox',
        seller: true,
        baseName: 'Sales',
      },
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile({bank_account_status: BANK_STATUSES.IN_SUPPORTED_COUNTRY}))
    vm.stats.makeReady(genCommissionStats())
    await wrapper.vm.$nextTick()
    await wrapper.find('.new-invoice-button').trigger('click')
    expect(vm.showNewInvoice).toBe(true)
    expect(vm.sellerName).toBe('Fox')
    expect(vm.invoiceEscrowEnabled).toBe(true)
    vm.newInvoice.fields.paid.update(true)
    await vm.$nextTick()
    expect(vm.invoiceEscrowEnabled).toBe(false)
  })
  test('Redirects to the right subview', async() => {
    await router.replace({
      name: 'Sales',
      params: {username: 'Fox'},
    })
    const mockPush = vi.spyOn(router, 'replace')
    setViewer(store, genUser())
    const wrapper = mount(Orders, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Fox',
        seller: true,
        baseName: 'Sales',
      },
    })
    await wrapper.vm.$nextTick()
    expect(mockPush).toHaveBeenCalledWith({
      name: 'CurrentSales',
      params: {username: 'Fox'},
    })
  })
  test('Does not ask for unneeded info if this is for orders instead of sales', async() => {
    setViewer(store, genUser())
    mockAxios.reset()
    const wrapper = mount(Orders, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Fox',
        seller: false,
        baseName: 'Orders',
      },
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(mockAxios.getReqByUrl(vm.stats.endpoint)).toBeUndefined()
  })
})
