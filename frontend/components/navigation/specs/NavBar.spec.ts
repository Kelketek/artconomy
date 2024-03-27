import {shallowMount, VueWrapper} from '@vue/test-utils'
import NavBar from '../NavBar.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import {genAnon, genUser} from '@/specs/helpers/fixtures.ts'
import {
  cleanUp, createTestRouter,
  mockRoutes,
  mount,
  rq,
  rs,
  vueSetup, VuetifyWrapped,
  waitFor, waitForSelector,
} from '@/specs/helpers/index.ts'
import mockAxios from '@/specs/helpers/mock-axios.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {nextTick} from 'vue'
import {createRouter, createWebHistory, Router} from 'vue-router'
import {setViewer} from '@/lib/lib.ts'

// Must use it directly, due to issues with package imports upstream.
let wrapper: VueWrapper<any>
let empty: VueWrapper<any>
let router: Router

const NavBarContainer = VuetifyWrapped(NavBar)

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
    router = createTestRouter(false)
    router.push('/')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Starts the notifications loop when a viewer is set and is real.', async() => {
    const dispatch = vi.spyOn(store, 'dispatch')
    wrapper = shallowMount(NavBar, vueSetup({
      store,
      extraPlugins: [router],
    }))
    await router.isReady()
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    await nextTick()
    expect((wrapper.vm as any).viewer.username).toBe('Fox')
    expect(dispatch).toHaveBeenCalledWith('notifications/startLoop')
  })
  test('Stops the notifications loop when a viewer is set and is anonymous.', async() => {
    const dispatch = vi.spyOn(store, 'dispatch')
    wrapper = shallowMount(NavBar, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.isReady()
    // Have to start as logged in to trigger the event.
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    await nextTick()
    dispatch.mockClear();
    (wrapper.vm as any).viewerHandler.user.setX(genAnon())
    await nextTick()
    expect(dispatch).toHaveBeenCalledWith('notifications/stopLoop')
  })
  test('Stops the notifications loop when destroyed.', async() => {
    const dispatch = vi.spyOn(store, 'dispatch')
    wrapper = shallowMount(NavBar, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.isReady()
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    await nextTick()
    dispatch.mockClear()
    wrapper.unmount()
    expect(dispatch).toHaveBeenCalledWith('notifications/stopLoop')
  })
  test('Generates a profile link', async() => {
    const user = genUser()
    user.username = 'Goober'
    user.artist_mode = false
    setViewer(store, user)
    wrapper = shallowMount(NavBar, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.isReady()
    await nextTick()
    expect((wrapper.vm as any).profileRoute).toEqual({
      name: 'AboutUser',
      params: {username: 'Goober'},
    })
  })
  test('Toggles the support form', async() => {
    setViewer(store, genUser())
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await nextTick()
    expect(store.state.showSupport).toBe(false)
    wrapper.find('.support-button').trigger('click')
    await nextTick()
    expect(store.state.showSupport).toBe(true)
  })
  test('Logs out a user', async() => {
    setViewer(store, genUser())
    await router.push({name: 'FAQ'})
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
    }))
    await router.isReady()
    await nextTick()
    mockAxios.reset()
    await waitForSelector(wrapper, '.logout-button')
    await wrapper.find('.logout-button').trigger('click')
    await nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/logout/', 'post', undefined, {}))
    mockAxios.mockResponseFor({url: '/api/profiles/logout/'}, rs(genAnon()))
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('Home'))
    expect(store.state.profiles!.viewerRawUsername).toEqual('_')
  })
  test('Loads the notifications view for an artist', async() => {
    setViewer(store, genUser({artist_mode: true}))
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.isReady()
    await nextTick()
    await wrapper.find('.notifications-button').trigger('click')
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SalesNotifications'))
    await wrapper.find('.notifications-button').trigger('click')
    await nextTick()
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('Reload'))
    expect(router.currentRoute.value.params).toEqual({path: '/notifications/sales/'})
  })
  test('Loads the notifications view for a non-artist', async() => {
    setViewer(store, genUser({artist_mode: false}))
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.isReady()
    await nextTick()
    await wrapper.find('.notifications-button').trigger('click')
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('CommunityNotifications'))
    await wrapper.find('.notifications-button').trigger('click')
    await nextTick()
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('Reload'))
    expect(router.currentRoute.value.params).toEqual({path: '/notifications/community/'})
  })
  test('Loads a login link', async() => {
    setViewer(store, genAnon())
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
    }))
    await nextTick()
    const vm = wrapper.findComponent(NavBar)!.vm as any
    expect(vm.loginLink).toEqual({name: 'Login', query: {next: '/'}})
    await router.replace({name: 'Login'})
    await waitFor(() => expect(vm.loginLink).toEqual({name: 'Login'}))
  })
  test('Sends you to the search page', async() => {
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.push('/')
    const field = wrapper.find('#nav-bar-search')
    await field.setValue('Stuff')
    await field.trigger('keyup')
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SearchProducts'))
    expect(router.currentRoute.value.query.q).toEqual('Stuff')
  })
  test('Sends you to the search page for recent products', async() => {
    setViewer(store, genUser())
    await router.isReady()
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.push('/')
    await waitForSelector(wrapper, '.who-is-open')
    await wrapper.find('.who-is-open').trigger('click')
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SearchProducts'))
    expect(router.currentRoute.value.query.q).toBeFalsy()
  })
  test('Sends you to the search page for recent art', async() => {
    setViewer(store, genUser())
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.isReady()
    await wrapper.find('.recent-art').trigger('click')
    await router.isReady()
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SearchSubmissions'))
  })
  test('Does not alter the route if we are already on a search page', async() => {
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['router-link'],
    }))
    await router.push({name: 'SearchSubmissions'})
    const field = wrapper.find('#nav-bar-search')
    await field.setValue('Stuff')
    await field.trigger('keyup')
    await nextTick()
    await router.isReady()
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SearchSubmissions'))
  })
})
