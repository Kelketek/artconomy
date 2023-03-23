import {createVuetify, mount, vueSetup} from '@/specs/helpers'
import TableDashboard from '@/components/views/table/TableDashboard.vue'
import {VueConstructor} from 'vue'
import {ArtStore, createStore} from '@/store'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Router, {RouterOptions} from 'vue-router'
import TableProducts from '@/components/views/table/TableProducts.vue'
import Vuetify from 'vuetify/lib'

let localVue: VueConstructor<Vue>
let store: ArtStore
let router: Router
let vuetify: Vuetify

describe('TableProducts.vue', () => {
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
        props: true,
      }, {
        path: '/table/products',
        name: 'TableProducts',
        component: Empty,
        props: true,
      }, {
        path: '/table/orders',
        name: 'TableOrders',
        component: Empty,
        props: true,
      }],
    }
    router = new Router(routes)
  })
  it('Mounts', async() => {
    await router.push({name: 'TableProducts'})
    mount(TableProducts, {localVue, store, router, vuetify})
  })
})
