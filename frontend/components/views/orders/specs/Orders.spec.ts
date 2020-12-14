import {cleanUp, createVuetify, docTarget, setViewer, vueSetup} from '@/specs/helpers'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Orders from '@/components/views/orders/Orders.vue'
import {genArtistProfile, genCommissionStats, genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {genPricing} from '@/lib/specs/helpers'
import OrderList from '@/components/views/orders/OrderList.vue'
import {BankStatus} from '@/store/profiles/types/BankStatus'
import mockAxios from '@/__mocks__/axios'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let router: Router
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('Orders.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'Sales',
        path: '/sales/:username/',
        props: true,
        component: Empty,
        children: [
          {name: 'CurrentSales', path: '/current', component: OrderList},
          {name: 'ArchivedSales', path: '/archived', component: OrderList},
          {name: 'CancelledSales', path: '/canceled', component: OrderList},
          {name: 'WaitingSales', path: '/waiting', component: OrderList},
        ],
      }, {
        name: 'Orders',
        path: '/orders/:username/',
        props: true,
        component: Empty,
        children: [
          {name: 'CurrentOrders', path: '/current', component: OrderList},
          {name: 'ArchivedOrders', path: '/archived', component: OrderList},
          {name: 'CancelledOrders', path: '/canceled', component: OrderList},
          {name: 'WaitingOrders', path: '/waiting', component: OrderList},
        ],
      }, {
        name: 'BuyAndSell',
        props: true,
        component: Empty,
        path: '/b-n-s',
      }, {
        name: 'Store',
        props: true,
        component: Empty,
        path: '/store/:username',
      }],
    })
    jest.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Sets up the order list', async() => {
    setViewer(store, genUser())
    const wrapper = mount(Orders, {
      localVue,
      store,
      vuetify,
      router,
      attachTo: docTarget(),
      propsData: {username: 'Fox', seller: true, baseName: 'Sales'},
    })
    const vm = wrapper.vm as any
    vm.pricing.makeReady(genPricing())
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile({bank_account_status: BankStatus.HAS_US_ACCOUNT}))
    await vm.$nextTick()
    expect(vm.closed).toBe(undefined)
  })
  it('Handles commission stats', async() => {
    setViewer(store, genUser())
    const wrapper = mount(Orders, {
      localVue,
      store,
      vuetify,
      router,
      attachTo: docTarget(),
      propsData: {username: 'Fox', seller: true, baseName: 'Sales'},
    })
    const vm = wrapper.vm as any
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile({bank_account_status: BankStatus.HAS_US_ACCOUNT}))
    vm.stats.setX(genCommissionStats())
    await vm.$nextTick()
    expect(vm.closed).toBe(false)
  })
  it('Triggers the invoicing form, and evaluates requisite functions', async() => {
    setViewer(store, genUser())
    const wrapper = mount(Orders, {
      localVue,
      store,
      vuetify,
      router,
      attachTo: docTarget(),
      propsData: {username: 'Fox', seller: true, baseName: 'Sales'},
    })
    const vm = wrapper.vm as any
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile({bank_account_status: BankStatus.HAS_US_ACCOUNT}))
    vm.stats.makeReady(genCommissionStats())
    wrapper.find('.ac-add-button').trigger('click')
    expect(vm.showNewInvoice).toBe(true)
    expect(vm.sellerName).toBe('Fox')
    expect(vm.invoiceEscrowDisabled).toBe(false)
    vm.newInvoice.fields.paid.update(true)
    await vm.$nextTick()
    expect(vm.invoiceEscrowDisabled).toBe(true)
  })
  it('Redirects to the right subview', async() => {
    await router.replace({name: 'Sales', params: {username: 'Fox'}})
    const mockPush = jest.spyOn(router, 'replace')
    setViewer(store, genUser())
    const wrapper = mount(Orders, {
      localVue,
      store,
      vuetify,
      router,
      attachTo: docTarget(),
      propsData: {username: 'Fox', seller: true, baseName: 'Sales'},
    })
    await wrapper.vm.$nextTick()
    expect(mockPush).toHaveBeenCalledWith({name: 'CurrentSales', params: {username: 'Fox'}})
  })
  it('Does not ask for unneeded info if this is for orders instead of sales', async() => {
    setViewer(store, genUser())
    mockAxios.reset()
    const wrapper = mount(Orders, {
      localVue,
      store,
      vuetify,
      router,
      attachTo: docTarget(),
      propsData: {username: 'Fox', seller: false, baseName: 'Orders'},
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(() => mockAxios.getReqByUrl(vm.stats.endpoint)).toThrow(
      Error('Could not find request for URL /api/sales/v1/account/Fox/sales/stats/'),
    )
  })
})
