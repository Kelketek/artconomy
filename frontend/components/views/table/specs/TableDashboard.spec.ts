import {createTestRouter, mount, vueSetup} from '@/specs/helpers/index.ts'
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
    router = createTestRouter()
  })
  test('Mounts', async() => {
    await router.push({name: 'TableDashboard'})
    mount(TableDashboard, vueSetup({
      store,
      router,
    }))
  })
})
