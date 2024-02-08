import {createRouter, createWebHistory, Router, RouteRecordRaw} from 'vue-router'
import {cleanUp, createVuetify, docTarget, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let routes: RouteRecordRaw[]
let router: Router

describe('AcLink.vue', () => {
  beforeEach(() => {
    store = createStore()
    routes = [{
      name: 'Test',
      path: '/test',
      component: Empty,
    }, {
      name: 'Home',
      path: '/',
      component: Empty,
    }]
    router = createRouter({
      history: createWebHistory(),
      routes,
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Navigates', async() => {
    wrapper = mount(AcLink, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {to: {name: 'Test'}},
    })
    const mockPush = vi.spyOn(wrapper.vm.$router, 'push')
    await wrapper.find('a').trigger('click')
    expect(mockPush).toHaveBeenCalledWith({name: 'Test'})
  })
  test('Makes links do new windows', async() => {
    const mockOpen = vi.spyOn(window, 'open')
    mockOpen.mockImplementationOnce(() => null)
    store.commit('setiFrame', true)
    wrapper = mount(AcLink, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {to: {name: 'Test'}},
    })
    await wrapper.find('a').trigger('click')
    expect(mockOpen).toHaveBeenCalledWith('/test', '_blank')
  })
})
