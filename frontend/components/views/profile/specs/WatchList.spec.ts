import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Router from 'vue-router'
import {cleanUp, createVuetify, docTarget, setViewer, vueSetup, mount} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import WatchList from '@/components/views/profile/WatchList.vue'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('WatchList.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'Profile',
        path: '/profiles/:username/',
        component: Empty,
        props: true,
      }, {
        name: 'AboutUser',
        path: '/profiles/:username/products/',
        component: Empty,
        props: true,
      }, {
        name: 'Dummy',
        path: '/dummy',
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
    // Need a route for the paginator to check page numbers on. Can be any.
    await router.push({name: 'Dummy'})
    wrapper = mount(WatchList, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {username: 'Fox', nameSpace: 'watching', endpoint: '/test/'},
      attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.watch.setList([genUser()])
    vm.watch.fetching = false
    vm.watch.ready = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.ac-avatar').exists()).toBe(true)
  })
})
