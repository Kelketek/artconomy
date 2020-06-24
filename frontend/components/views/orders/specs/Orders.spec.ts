import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {Vuetify} from 'vuetify'
import Orders from '@/components/views/orders/Orders.vue'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'
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
        ],
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
  })
})
