import {createVuetify, mount, vueSetup} from '@/specs/helpers'
import TableDashboard from '@/components/views/table/TableDashboard.vue'
import {VueConstructor} from 'vue'
import {ArtStore, createStore} from '@/store'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Router, {RouterOptions} from 'vue-router'
import Vuetify from 'vuetify/lib'

let localVue: VueConstructor<Vue>
let store: ArtStore
let router: Router
let vuetify: Vuetify

describe('TableDashboard.vue', () => {
  beforeEach(() => {
    localVue = vueSetup()
    localVue.use(Router)
    vuetify = createVuetify()
    store = createStore()
    const routes: RouterOptions = {
      mode: 'history',
      routes: [{
        path: '/table',
        name: 'TableDashboard',
        component: Empty,
      }, {
        path: '/table/products',
        name: 'TableProducts',
        component: Empty,
      }, {
        path: '/table/orders',
        name: 'TableOrders',
        component: Empty,
      }, {
        path: '/table/invoices/',
        name: 'TableInvoices',
        component: Empty,
      }],
    }
    router = new Router(routes)
  })
  it('Mounts', async() => {
    await router.push({name: 'TableDashboard'})
    mount(TableDashboard, {localVue, store, router, vuetify})
  })
})
