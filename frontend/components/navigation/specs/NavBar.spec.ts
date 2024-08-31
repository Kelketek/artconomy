import {shallowMount, VueWrapper} from '@vue/test-utils'
import NavBar from '../NavBar.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import {genAnon, genUser} from '@/specs/helpers/fixtures.ts'
import {
  cleanUp, createTestRouter,
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
import {Router} from 'vue-router'
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
    router = createTestRouter()
    router.push('/')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Generates a profile link', async() => {
    const user = genUser()
    user.username = 'Goober'
    user.artist_mode = false
    setViewer({ store, user })
    wrapper = shallowMount(NavBar, vueSetup({
      store,
      router,
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
    setViewer({ store, user: genUser() })
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      router,
      stubs: ['router-link'],
    }))
    await nextTick()
    expect(store.state.showSupport).toBe(false)
    await wrapper.find('.support-button').trigger('click')
    await nextTick()
    expect(store.state.showSupport).toBe(true)
  })
  test('Logs out a user', async() => {
    setViewer({ store, user: genUser() })
    await router.push({name: 'FAQ'})
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      router,
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
  test('Loads the notifications view', async() => {
    setViewer({ store, user: genUser({ artist_mode: true }) })
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      router,
      stubs: ['router-link'],
    }))
    await router.isReady()
    await nextTick()
    await wrapper.find('.notifications-button').trigger('click')
    await waitFor(() => expect(wrapper.find('.message-center.v-navigation-drawer--active').exists()).toBe(true))
  })
  test('Loads a login link', async() => {
    setViewer({ store, user: genAnon() })
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      router,
    }))
    await nextTick()
    const vm = wrapper.findComponent(NavBar)!.vm as any
    expect(vm.loginLink).toEqual({
      name: 'Login',
      query: {next: '/'},
    })
    await router.replace({name: 'Login'})
    await waitFor(() => expect(vm.loginLink).toEqual({name: 'Login'}))
  })
  test('Sends you to the search page', async() => {
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      router,
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
    setViewer({ store, user: genUser() })
    await router.isReady()
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      router,
      stubs: ['router-link'],
    }))
    await router.push('/')
    await waitForSelector(wrapper, '.who-is-open')
    await wrapper.find('.who-is-open').trigger('click')
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SearchProducts'))
    expect(router.currentRoute.value.query.q).toBeFalsy()
  })
  test('Sends you to the search page for recent art', async() => {
    setViewer({ store, user: genUser() })
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      router,
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
      router,
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
