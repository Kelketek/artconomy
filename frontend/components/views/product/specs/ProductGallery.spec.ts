import {ArtStore, createStore} from '@/store/index.ts'
import {mount, vueSetup} from '@/specs/helpers/index.ts'
import {createRouter, createWebHistory, Router} from 'vue-router'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import ProductGallery from '@/components/views/product/ProductGallery.vue'
import {genProduct, genUser} from '@/specs/helpers/fixtures.ts'
import {beforeEach, describe, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import {nextTick} from 'vue'

let store: ArtStore
let router: Router

const routes = [
  {
    path: '/store/:username/product/:productId',
    name: 'Product',
    component: Empty,
    props: true,
    children: [{
      path: 'gallery/',
      name: 'ProductGallery',
      component: Empty,
      props: true,
    }],
  },
  {
    path: '/',
    name: 'Home',
    component: Empty,
  },
]

describe('ProductGallery', () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes,
    })
  })
  test('Mounts', async() => {
    setViewer({ store, user: genUser() })
    const wrapper = mount(
      ProductGallery, {
        ...vueSetup({
          store,
          router,
        }),
        props: {
          username: 'Fox',
          productId: '5',
        },
      })
    const vm = wrapper.vm as any
    vm.product.makeReady(genProduct())
    await nextTick()
  })
})
