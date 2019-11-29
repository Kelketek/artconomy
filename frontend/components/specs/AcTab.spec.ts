import Vue from 'vue'
import Router from 'vue-router'
import {vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import AcTab from '@/components/AcTab.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router

describe('AcTab.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = new Router({mode: 'history',
      routes: [{
        name: 'Place',
        component: Empty,
        path: '/place/',
      }]})
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Renders list tab information', async() => {
    const list = mount(Empty, {localVue, store}).vm.$getList('stuff', {endpoint: '/'})
    list.fetching = false
    list.ready = true
    wrapper = mount(AcTab, {
      localVue,
      store,
      router,
      propsData: {trackPages: true, to: {name: 'Place'}, list},
      attachToDocument: false,
      sync: true,
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
      propsData: {trackPages: false, to: {name: 'Place'}},
      attachToDocument: false,
      sync: true,
    })
    const vm = wrapper.vm as any
    expect(vm.destination).toEqual({name: 'Place'})
  })
  it('Links to nowhere', async() => {
    wrapper = mount(AcTab, {
      localVue,
      store,
      router,
      propsData: {},
      attachToDocument: false,
      sync: true,
    })
    const vm = wrapper.vm as any
    expect(vm.destination).toBe(undefined)
  })
})
