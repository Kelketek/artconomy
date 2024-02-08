import {mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {createRouter, createWebHistory, Router, RouterOptions} from 'vue-router'
import TableProducts from '@/components/views/table/TableProducts.vue'
import {beforeEach, describe, test} from 'vitest'

let store: ArtStore
let router: Router

describe('TableProducts.vue', () => {
  beforeEach(() => {
    store = createStore()
    const routes: RouterOptions = {
      history: createWebHistory(),
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
    router = createRouter(routes)
  })
  test('Mounts', async() => {
    await router.push({name: 'TableProducts'})
    mount(TableProducts, vueSetup({
      store,
      extraPlugins: [router],
    }))
  })
})
