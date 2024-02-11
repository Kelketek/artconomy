import {shallowMount, VueWrapper} from '@vue/test-utils'
import NavBar from '../NavBar.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {
  cleanUp,
  flushPromises,
  genAnon,
  mockRoutes,
  mount,
  rq,
  rs,
  setViewer,
  vueSetup,
  waitFor,
} from '@/specs/helpers/index.ts'
import mockAxios from '@/specs/helpers/mock-axios.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import NavBarContainer from '@/components/navigation/specs/NavBarContainer.vue'
import {nextTick, reactive} from 'vue'
import {createRouter, createWebHistory, Router} from 'vue-router'

// Must use it directly, due to issues with package imports upstream.
let wrapper: VueWrapper<any>
let empty: VueWrapper<any>
let router: Router

describe('NavBar.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    empty = mount(Empty, vueSetup({store}))
    empty.vm.$getForm('search', {
      endpoint: '/',
      fields: {q: {value: ''}},
    })
    router = createRouter({
      history: createWebHistory(),
      routes: mockRoutes,
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  // test('Starts the notifications loop when a viewer is set and is real.', async() => {
  //   const dispatch = vi.spyOn(store, 'dispatch')
  //   wrapper = shallowMount(NavBar, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //   }))
  //   await router.isReady()
  //   const vm = wrapper.vm as any
  //   vm.viewerHandler.user.makeReady(genUser())
  //   await wrapper.vm.$nextTick()
  //   expect((wrapper.vm as any).viewer.username).toBe('Fox')
  //   expect(dispatch).toHaveBeenCalledWith('notifications/startLoop')
  // })
  // test('Stops the notifications loop when a viewer is set and is anonymous.', async() => {
  //   const dispatch = vi.spyOn(store, 'dispatch')
  //   wrapper = shallowMount(NavBar, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await router.isReady()
  //   // Have to start as logged in to trigger the event.
  //   const vm = wrapper.vm as any
  //   vm.viewerHandler.user.makeReady(genUser())
  //   await nextTick()
  //   dispatch.mockClear();
  //   (wrapper.vm as any).viewerHandler.user.setX(genAnon())
  //   await wrapper.vm.$nextTick()
  //   expect(dispatch).toHaveBeenCalledWith('notifications/stopLoop')
  // })
  // test('Stops the notifications loop when destroyed.', async() => {
  //   const dispatch = vi.spyOn(store, 'dispatch')
  //   wrapper = shallowMount(NavBar, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await router.isReady()
  //   const vm = wrapper.vm as any
  //   vm.viewerHandler.user.makeReady(genUser())
  //   await nextTick()
  //   dispatch.mockClear()
  //   wrapper.unmount()
  //   expect(dispatch).toHaveBeenCalledWith('notifications/stopLoop')
  // })
  // test('Generates a profile link', async() => {
  //   const user = genUser()
  //   user.username = 'Goober'
  //   user.artist_mode = false
  //   setViewer(store, user)
  //   wrapper = shallowMount(NavBar, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await router.isReady()
  //   await nextTick()
  //   expect((wrapper.vm as any).profileRoute).toEqual({
  //     name: 'AboutUser',
  //     params: {username: 'Goober'},
  //   })
  // })
  // test('Toggles the support form', async() => {
  //   setViewer(store, genUser())
  //   wrapper = mount(NavBarContainer, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await wrapper.vm.$nextTick()
  //   expect(store.state.showSupport).toBe(false)
  //   wrapper.find('.support-button').trigger('click')
  //   await nextTick()
  //   expect(store.state.showSupport).toBe(true)
  // })
  // test('Logs out a user', async() => {
  //   setViewer(store, genUser())
  //   wrapper = mount(NavBarContainer, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await router.isReady()
  //   await nextTick()
  //   mockAxios.reset()
  //   wrapper.find('.logout-button').trigger('click')
  //   await wrapper.vm.$nextTick()
  //   expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/logout/', 'post', undefined, {}))
  //   mockAxios.mockResponse(rs(genAnon()))
  //   await flushPromises()
  //   expect(store.state.profiles!.viewerRawUsername).toEqual('_')
  //   expect(router.currentRoute.value.name).toEqual('Home')
  // })
  // test('Loads the notifications view', async() => {
  //   setViewer(store, genUser())
  //   wrapper = mount(NavBarContainer, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await router.isReady()
  //   await wrapper.vm.$nextTick()
  //   await wrapper.find('.notifications-button').trigger('click')
  //   await waitFor(() => expect(router.currentRoute.value.name).toEqual('CommunityNotifications'))
  //   const vm = wrapper.vm.$refs.nav as any
  //   await wrapper.find('.notifications-button').trigger('click')
  //   await vm.$nextTick()
  //   expect(router.currentRoute.value.name).toEqual('Reload')
  //   expect(router.currentRoute.value.params).toEqual({path: '/notifications/community/'})
  // })
  // test('Loads a login link', async() => {
  //   setViewer(store, genAnon())
  //   wrapper = mount(NavBarContainer, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await wrapper.vm.$nextTick()
  //   const vm = wrapper.vm.$refs.nav as any
  //   expect(wrapper.find('.nav-login-item').attributes()['href']).toEqual(router.resolve({name: 'Login', query: {next: '/'}}).fullPath)
  //   await router.replace({name: 'Login'})
  //   await vm.$nextTick()
  //   expect(wrapper.find('.nav-login-item').attributes()['href']).toEqual(router.resolve({name: 'Login'}).fullPath)
  // })
  test('Sends you to the search page', async() => {
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.isReady()
    const field = wrapper.find('#nav-bar-search')
    await field.setValue('Stuff')
    await field.trigger('keyup')
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SearchProducts'))
    expect(router.currentRoute.value.query).toEqual({q: 'Stuff', page: '1', size: '24'})
  })
  // test('Sends you to the search page for recent products', async() => {
  //   setViewer(store, genUser())
  //   wrapper = mount(NavBarContainer, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await wrapper.vm.$nextTick()
  //   await wrapper.find('.who-is-open').trigger('click')
  //   await router.isReady()
  //   expect(router.currentRoute.value.name).toEqual('SearchProducts')
  //   expect(router.currentRoute.value.query).toEqual({q: ''})
  // })
  // test('Sends you to the search page for recent art', async() => {
  //   setViewer(store, genUser())
  //   wrapper = mount(NavBarContainer, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await router.isReady()
  //   await wrapper.find('.recent-art').trigger('click')
  //   await router.isReady()
  //   expect(router.currentRoute.value.name).toEqual('SearchSubmissions')
  // })
  // test('Does not alter the route if we are already on a search page', async() => {
  //   wrapper = mount(NavBarContainer, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //     stubs: ['router-link'],
  //   }))
  //   await router.push({name: 'SearchSubmissions'})
  //   const field = wrapper.find('#nav-bar-search')
  //   await field.setValue('Stuff')
  //   await field.trigger('keyup')
  //   await nextTick()
  //   await router.isReady()
  //   expect(router.currentRoute.value.name).toEqual('SearchSubmissions')
  // })
})
