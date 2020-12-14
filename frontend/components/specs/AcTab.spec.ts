import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Router from 'vue-router'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import AcTab from '@/components/AcTab.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('AcTab.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'Place',
        component: Empty,
        path: '/place/',
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Renders list tab information', async() => {
    const list = mount(Empty, {localVue, store}).vm.$getList('stuff', {endpoint: '/'})
    list.fetching = false
    list.ready = true
    wrapper = mount(AcTab, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {trackPages: true, to: {name: 'Place'}, list},

    })
    const vm = wrapper.vm as any
    expect(vm.destination).toEqual({name: 'Place'})
    list.currentPage = 3
    list.response = {count: 24, size: 5}
    list.fetching = true
    list.ready = true
    await wrapper.vm.$nextTick()
    expect(vm.destination).toEqual({name: 'Place', query: {page: '3'}})
  })
  it('Links to a destination', async() => {
    wrapper = mount(AcTab, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {trackPages: false, to: {name: 'Place'}},

    })
    const vm = wrapper.vm as any
    expect(vm.destination).toEqual({name: 'Place'})
  })
  it('Links to nowhere', async() => {
    wrapper = mount(AcTab, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {},

    })
    const vm = wrapper.vm as any
    expect(vm.destination).toBe(undefined)
  })
})
