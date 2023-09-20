import {ArtStore, createStore} from '@/store'
import {createVuetify, mount, setViewer, vueSetup} from '@/specs/helpers'
import {VueConstructor} from 'vue'
import Router, {RouterOptions} from 'vue-router'
import Vuetify from 'vuetify/lib'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import ProductGallery from '@/components/views/product/ProductGallery.vue'
import {genProduct, genUser} from '@/specs/helpers/fixtures'
import mockAxios from '@/specs/helpers/mock-axios'

let localVue: VueConstructor
let store: ArtStore
let router: Router
let vuetify: Vuetify

const routes: RouterOptions = {
  mode: 'history',
  routes: [{
    path: '/store/{username}/product/{productId}',
    name: 'Product',
    component: Empty,
    props: true,
    children: [{
      path: 'gallery/',
      name: 'ProductGallery',
      component: Empty,
      props: true,
    }],
  }],
}

describe('ProductGallery', () => {
  beforeEach(() => {
    localVue = vueSetup()
    localVue.use(Router)
    store = createStore()
    vuetify = createVuetify()
    router = new Router(routes)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    const wrapper = mount(
      ProductGallery, {
        store,
        vuetify,
        localVue,
        router,
        propsData: {username: 'Fox', productId: '5'},
      })
    const vm = wrapper.vm as any
    vm.product.makeReady(genProduct())
    await wrapper.vm.$nextTick()
  })
})
