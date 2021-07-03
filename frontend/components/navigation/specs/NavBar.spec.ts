import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {shallowMount, Wrapper} from '@vue/test-utils'
import NavBar from '../NavBar.vue'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import {
  cleanUp,
  createVuetify, docTarget,
  flushPromises,
  genAnon,
  rq,
  rs,
  setViewer,
  vueSetup,
  mount,
} from '@/specs/helpers'
import mockAxios from '@/specs/helpers/mock-axios'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {useMockStorage} from '@/lib/specs/helpers'

// Must use it directly, due to issues with package imports upstream.
const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let empty: Wrapper<Vue>
let vuetify: Vuetify

describe('NavBar.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    mockAxios.reset()
    store = createStore()
    jest.useFakeTimers()
    vuetify = createVuetify()
    empty = mount(Empty, {localVue, store})
    empty.vm.$getForm('search', {endpoint: '/', fields: {q: {value: ''}}})
    useMockStorage()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Starts with the drawer closed on small screens', async() => {
    (window as any).innerWidth = 300
    dispatchEvent(new Event('resize'))
    await jest.runAllTimers()
    wrapper = shallowMount(NavBar, {
      store,
      localVue,
      vuetify,
      propsData: {initialState: null},
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}},
      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).drawer).toBe(false)
  })
  it('Starts with the drawer open on large screens', async() => {
    (window as any).innerWidth = 1500
    dispatchEvent(new Event('resize'))
    await jest.runAllTimers()
    wrapper = shallowMount(NavBar, {
      store,
      localVue,
      vuetify,
      propsData: {initialState: null},
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}},
      attachTo: docTarget(),
    })
    expect((wrapper.vm as any).drawer).toBe(true)
  })
  it('Starts the notifications loop when a viewer is set and is real.', async() => {
    const dispatch = jest.spyOn(store, 'dispatch')
    wrapper = shallowMount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}},
    })
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).viewer.username).toBe('Fox')
    expect(dispatch).toHaveBeenCalledWith('notifications/startLoop')
  })
  it('Stops the notifications loop when a viewer is set and is anonymous.', async() => {
    const dispatch = jest.spyOn(store, 'dispatch')
    wrapper = mount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}},
      stubs: ['router-link'],
      attachTo: docTarget(),
    })
    // Have to start as logged in to trigger the event.
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    await wrapper.vm.$nextTick()
    dispatch.mockClear();
    (wrapper.vm as any).viewerHandler.user.setX(genAnon())
    await wrapper.vm.$nextTick()
    expect(dispatch).toHaveBeenCalledWith('notifications/stopLoop')
  })
  it('Stops the notifications loop when destroyed.', async() => {
    const dispatch = jest.spyOn(store, 'dispatch')
    wrapper = shallowMount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}},

    })
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    await wrapper.vm.$nextTick()
    dispatch.mockClear()
    wrapper.destroy()
    expect(dispatch).toHaveBeenCalledWith('notifications/stopLoop')
  })
  it('Handles the drawer preference via local storage', async() => {
    wrapper = shallowMount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}},
      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    vm.drawer = false
    expect(vm.drawer).toBe(false)
    vm.drawer = null
    await wrapper.vm.$nextTick()
    expect(vm.drawer).toBe(true)
    wrapper.destroy()
  })
  it('Generates a profile link', async() => {
    const user = genUser()
    user.username = 'Goober'
    user.artist_mode = false
    setViewer(store, user)
    wrapper = shallowMount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}},

    })
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).profileRoute).toEqual({name: 'AboutUser', params: {username: 'Goober'}})
  })
  it('Toggles the support form', async() => {
    setViewer(store, genUser())
    wrapper = mount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}},
      stubs: ['router-link'],

      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    expect(store.state.showSupport).toBe(false)
    wrapper.find('.support-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.showSupport).toBe(true)
  })
  it('Logs out a user', async() => {
    setViewer(store, genUser())
    const mockPush = jest.fn()
    wrapper = mount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}, $router: {push: mockPush}},
      stubs: ['router-link'],

      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.logout-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockAxios.post).toHaveBeenCalledWith(...rq('/api/profiles/v1/logout/', 'post', undefined, {}))
    mockAxios.mockResponse(rs(genAnon()))
    await flushPromises()
    expect((wrapper.vm as any).viewerName).toBe('')
    expect(mockPush).toHaveBeenCalledWith({name: 'Home'})
  })
  it('Loads the notifications view', async() => {
    setViewer(store, genUser())
    const mockPush = jest.fn()
    const mockReplace = jest.fn()
    wrapper = mount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}, $router: {push: mockPush, replace: mockReplace}},
      stubs: ['router-link'],

      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.notifications-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockPush).toHaveBeenCalledWith({name: 'CommunityNotifications'})
    const vm = wrapper.vm as any
    vm.$route = {name: 'CommunityNotifications', params: {}, path: '/notifications/community/'}
    wrapper.find('.notifications-button').trigger('click')
    await vm.$nextTick()
    expect(mockReplace).toHaveBeenCalledWith({name: 'Reload', params: {path: '/notifications/community/'}})
  })
  it('Loads a login link', async() => {
    setViewer(store, genUser())
    wrapper = mount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}},
      stubs: ['router-link'],

      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.loginLink).toEqual({name: 'Login', params: {tabName: 'login'}, query: {next: '/'}})
    vm.$route.name = 'Login'
    await vm.$nextTick()
    expect(vm.loginLink).toEqual({name: 'Login', params: {tabName: 'login'}})
  })
  it('Sends you to the search page', async() => {
    const mockPush = jest.fn()
    wrapper = mount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}, $router: {push: mockPush}},
      stubs: ['router-link'],

      attachTo: docTarget(),
    })
    const field = wrapper.find('#nav-bar-search')
    field.setValue('Stuff')
    field.trigger('keyup')
    expect(mockPush).toHaveBeenCalledWith({name: 'SearchProducts', query: {q: 'Stuff'}})
  })
  it('Sends you to the search page for recent products', async() => {
    setViewer(store, genUser())
    const mockPush = jest.fn()
    wrapper = mount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}, $router: {push: mockPush}},
      stubs: ['router-link'],

      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    wrapper.find('.who-is-open').trigger('click')
    expect(mockPush).toHaveBeenCalledWith({name: 'SearchProducts'})
  })
  it('Sends you to the search page for recent art', async() => {
    setViewer(store, genUser())
    const mockPush = jest.fn()
    wrapper = mount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', name: 'Home', path: '/'}, $router: {push: mockPush}},
      stubs: ['router-link'],

      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    wrapper.find('.recent-art').trigger('click')
    expect(mockPush).toHaveBeenCalledWith({name: 'SearchSubmissions'})
  })
  it('Does not alter the route if we are already on a search page', async() => {
    const mockPush = jest.fn()
    wrapper = mount(NavBar, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/search/products', name: 'SearchProducts', path: '/'}, $router: {push: mockPush}},
      stubs: ['router-link'],

      attachTo: docTarget(),
    })
    const field = wrapper.find('#nav-bar-search')
    field.setValue('Stuff')
    field.trigger('keyup')
    expect(mockPush).not.toHaveBeenCalled()
  })
})
