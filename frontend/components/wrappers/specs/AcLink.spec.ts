import Vue from 'vue'
import Router, {RouteConfig} from 'vue-router'
import {vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import AcLink from '@/components/wrappers/AcLink.vue'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let routes: RouteConfig[]
let router: Router

describe('AcLink.vue', () => {
  beforeEach(() => {
    store = createStore()
    routes = [{
      name: 'Test',
      path: '/test',
      component: Empty,
    }]
    router = new Router({mode: 'history', routes})
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Navigates', async() => {
    wrapper = mount(AcLink, {
      localVue, store, router, propsData: {to: {name: 'Test'}}, sync: false, attachToDocument: true,
    })
    const mockPush = jest.spyOn(wrapper.vm.$router, 'push')
    wrapper.find('a').trigger('click')
    expect(mockPush).toHaveBeenCalledWith({name: 'Test'})
  })
  it('Makes links do new windows', async() => {
    const mockOpen = jest.spyOn(window, 'open')
    mockOpen.mockImplementationOnce(() => null)
    store.commit('setiFrame', true)
    wrapper = mount(AcLink, {
      localVue, store, router, propsData: {to: {name: 'Test'}}, sync: false, attachToDocument: true,
    })
    wrapper.find('a').trigger('click')
    expect(mockOpen).toHaveBeenCalledWith('/test', '_blank')
  })
})
