import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {Vuetify} from 'vuetify'
import Orders from '@/components/views/orders/Orders.vue'
import {genArtistProfile, genCommissionStats, genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {genPricing} from '@/lib/specs/helpers'
import OrderList from '@/components/views/orders/OrderList.vue'
import {BankStatus} from '@/store/profiles/types/BankStatus'

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
      attachToDocument: true,
      sync: false,
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
      attachToDocument: true,
      sync: false,
      propsData: {username: 'Fox', seller: true, baseName: 'Sales'},
    })
    const vm = wrapper.vm as any
    vm.viewerHandler.artistProfile.makeReady(genArtistProfile({bank_account_status: BankStatus.HAS_US_ACCOUNT}))
    vm.stats.setX(genCommissionStats())
    await vm.$nextTick()
    expect(vm.closed).toBe(false)
  })
  // it('Loads an invoicing form', async() => {
  //   setViewer(store, genUser())
  //   const wrapper = mount(Orders, {
  //     localVue,
  //     store,
  //     vuetify,
  //     router,
  //     attachToDocument: true,
  //     sync: false,
  //     propsData: {username: 'Fox', seller: true, baseName: 'Sales'},
  //   })
  //   const vm = wrapper.vm as any
  //   vm.viewerHandler.artistProfile.makeReady(genArtistProfile({bank_account_status: BankStatus.HAS_US_ACCOUNT}))
  //   vm.stats.makeReady(genCommissionStats())
  //   wrapper.find('.ac-add-button').trigger('click')
  //   await vm.$nextTick()
  //   console.log(wrapper.html())
  //   expect(vm.showNewInvoice).toBe(true)
  // })
})
