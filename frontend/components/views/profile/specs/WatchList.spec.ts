import Vue from 'vue'
import Router from 'vue-router'
import {cleanUp, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {FormController} from '@/store/forms/form-controller'
import WatchList from '@/components/views/profile/WatchList.vue'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let searchForm: FormController
let router: Router

describe('WatchList.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'Profile',
        path: '/profiles/:username/',
        component: Empty,
        props: true,
      }, {
        name: 'Products',
        path: '/profiles/:username/products/',
        component: Empty,
        props: true,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts and loads a watchlist', async() => {
    setViewer(store, genUser())
    const wrapper = mount(WatchList, {
      localVue,
      store,
      router,
      propsData: {username: 'Fox', nameSpace: 'watching', endpoint: '/test/'},
      attachToDocument: true,
      sync: false,
    })
    const vm = wrapper.vm as any
    vm.watch.setList([genUser()])
    vm.watch.fetching = false
    vm.watch.ready = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.ac-avatar').exists()).toBe(true)
  })
})
