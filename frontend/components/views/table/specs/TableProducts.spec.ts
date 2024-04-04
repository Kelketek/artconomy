import {createTestRouter, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {Router} from 'vue-router'
import TableProducts from '@/components/views/table/TableProducts.vue'
import {beforeEach, describe, test} from 'vitest'

let store: ArtStore
let router: Router

describe('TableProducts.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = createTestRouter()
  })
  test('Mounts', async() => {
    await router.push({name: 'TableProducts'})
    mount(TableProducts, vueSetup({
      store,
      router,
    }))
  })
})
