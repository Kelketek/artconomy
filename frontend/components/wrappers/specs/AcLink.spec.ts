import Vue from 'vue'
import Router, {RouteConfig} from 'vue-router'
import {cleanUp, createVuetify, docTarget, vueSetup, mount} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let routes: RouteConfig[]
let router: Router
let vuetify: Vuetify

describe('AcLink.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    routes = [{
      name: 'Test',
      path: '/test',
      component: Empty,
    }]
    router = new Router({mode: 'history', routes})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Navigates', async() => {
    wrapper = mount(AcLink, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {to: {name: 'Test'}},

      attachTo: docTarget(),
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
      localVue,
      store,
      router,
      vuetify,
      propsData: {to: {name: 'Test'}},

      attachTo: docTarget(),
    })
    wrapper.find('a').trigger('click')
    expect(mockOpen).toHaveBeenCalledWith('/test', '_blank')
  })
})
