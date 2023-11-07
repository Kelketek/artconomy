import {ArtStore, createStore} from '@/store'
import {mount, setViewer, vueSetup} from '@/specs/helpers'
import {createRouter, createWebHistory, Router} from 'vue-router'
import Empty from '@/specs/helpers/dummy_components/empty'
import ProductGallery from '@/components/views/product/ProductGallery.vue'
import {genProduct, genUser} from '@/specs/helpers/fixtures'
import {beforeEach, describe, test} from 'vitest'

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
    setViewer(store, genUser())
    const wrapper = mount(
      ProductGallery, {
        ...vueSetup({
          store,
          extraPlugins: [router],
        }),
        props: {
          username: 'Fox',
          productId: '5',
        },
      })
    const vm = wrapper.vm as any
    vm.product.makeReady(genProduct())
    await wrapper.vm.$nextTick()
  })
})
