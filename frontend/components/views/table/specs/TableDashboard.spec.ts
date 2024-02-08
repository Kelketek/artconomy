import {mount, vueSetup} from '@/specs/helpers/index.ts'
import TableDashboard from '@/components/views/table/TableDashboard.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {createRouter, createWebHistory, Router, RouterOptions} from 'vue-router'
import {beforeEach, describe, test} from 'vitest'

let store: ArtStore
let router: Router

describe('TableDashboard.vue', () => {
  beforeEach(() => {
    store = createStore()
    const routes: RouterOptions = {
      history: createWebHistory(),
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
    router = createRouter(routes)
  })
  test('Mounts', async() => {
    await router.push({name: 'TableDashboard'})
    mount(TableDashboard, vueSetup({
      store,
      extraPlugins: [router],
    }))
  })
})
