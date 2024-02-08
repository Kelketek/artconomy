import {shallowMount, VueWrapper} from '@vue/test-utils'
import NavBar from '../NavBar.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {
  cleanUp,
  flushPromises,
  genAnon,
  mount,
  rq,
  rs,
  setViewer,
  vueSetup,
} from '@/specs/helpers/index.ts'
import mockAxios from '@/specs/helpers/mock-axios.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {initDrawerValue} from '@/lib/lib.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import NavBarContainer from '@/components/navigation/specs/NavBarContainer.vue'
import {reactive} from 'vue'

// Must use it directly, due to issues with package imports upstream.
let wrapper: VueWrapper<any>
let empty: VueWrapper<any>

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
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Starts the notifications loop when a viewer is set and is real.', async() => {
    const dispatch = vi.spyOn(store, 'dispatch')
    wrapper = shallowMount(NavBar, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
      },
    }))
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).viewer.username).toBe('Fox')
    expect(dispatch).toHaveBeenCalledWith('notifications/startLoop')
  })
  test('Stops the notifications loop when a viewer is set and is anonymous.', async() => {
    const dispatch = vi.spyOn(store, 'dispatch')
    wrapper = shallowMount(NavBar, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
      },
      stubs: ['router-link'],
    }))
    // Have to start as logged in to trigger the event.
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    await wrapper.vm.$nextTick()
    dispatch.mockClear();
    (wrapper.vm as any).viewerHandler.user.setX(genAnon())
    await wrapper.vm.$nextTick()
    expect(dispatch).toHaveBeenCalledWith('notifications/stopLoop')
  })
  test('Stops the notifications loop when destroyed.', async() => {
    const dispatch = vi.spyOn(store, 'dispatch')
    wrapper = shallowMount(NavBar, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
      },
      stubs: ['router-link'],
    }))
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    await wrapper.vm.$nextTick()
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
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
      },
      stubs: ['router-link'],
    }))
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).profileRoute).toEqual({
      name: 'AboutUser',
      params: {username: 'Goober'},
    })
  })
  test('Toggles the support form', async() => {
    setViewer(store, genUser())
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
      },
      stubs: ['router-link'],
    }))
    await wrapper.vm.$nextTick()
    expect(store.state.showSupport).toBe(false)
    wrapper.find('.support-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.showSupport).toBe(true)
  })
  test('Logs out a user', async() => {
    setViewer(store, genUser())
    const mockPush = vi.fn()
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
        $router: {push: mockPush},
      },
      stubs: ['router-link'],
    }))
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.logout-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(rq('/api/profiles/logout/', 'post', undefined, {}))
    mockAxios.mockResponse(rs(genAnon()))
    await flushPromises()
    expect((wrapper.vm as any).$refs.nav.viewerName).toBe('')
    expect(mockPush).toHaveBeenCalledWith({name: 'Home'})
  })
  test('Loads the notifications view', async() => {
    setViewer(store, genUser())
    const mockPush = vi.fn()
    const mockReplace = vi.fn()
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
        $router: {
          push: mockPush,
          replace: mockReplace,
        },
      },
      stubs: ['router-link'],
    }))
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.notifications-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockPush).toHaveBeenCalledWith({name: 'CommunityNotifications'})
    const vm = wrapper.vm.$refs.nav as any
    vm.$route = {
      name: 'CommunityNotifications',
      params: {},
      path: '/notifications/community/',
    }
    wrapper.find('.notifications-button').trigger('click')
    await vm.$nextTick()
    expect(mockReplace).toHaveBeenCalledWith({
      name: 'Reload',
      params: {path: '/notifications/community/'},
    })
  })
  test('Loads a login link', async() => {
    setViewer(store, genUser())
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      mocks: {
        $route: reactive({
          fullPath: '/',
          name: 'Home',
          path: '/',
        }),
      },
      stubs: ['router-link'],
    }))
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm.$refs.nav as any
    expect(vm.loginLink).toEqual({
      name: 'Login',
      query: {next: '/'},
    })
    vm.$route.name = 'Login'
    await vm.$nextTick()
    expect(vm.loginLink).toEqual({
      name: 'Login',
    })
  })
  test('Sends you to the search page', async() => {
    const mockPush = vi.fn()
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
        $router: {push: mockPush},
      },
      stubs: ['router-link'],
    }))
    const field = wrapper.find('#nav-bar-search')
    await field.setValue('Stuff')
    await field.trigger('keyup')
    expect(mockPush).toHaveBeenCalledWith({
      name: 'SearchProducts',
      query: {q: 'Stuff'},
    })
  })
  test('Sends you to the search page for recent products', async() => {
    setViewer(store, genUser())
    const mockPush = vi.fn()
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
        $router: {push: mockPush},
      },
      stubs: ['router-link'],
    }))
    await wrapper.vm.$nextTick()
    await wrapper.find('.who-is-open').trigger('click')
    expect(mockPush).toHaveBeenCalledWith({
      name: 'SearchProducts',
      query: {q: ''},
    })
  })
  test('Sends you to the search page for recent art', async() => {
    setViewer(store, genUser())
    const mockPush = vi.fn()
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/',
          name: 'Home',
          path: '/',
        },
        $router: {push: mockPush},
      },
      stubs: ['router-link'],
    }))
    await wrapper.vm.$nextTick()
    wrapper.find('.recent-art').trigger('click')
    expect(mockPush).toHaveBeenCalledWith({
      name: 'SearchSubmissions',
      query: {q: ''},
    })
  })
  test('Does not alter the route if we are already on a search page', async() => {
    const mockPush = vi.fn()
    wrapper = mount(NavBarContainer, vueSetup({
      store,
      mocks: {
        $route: {
          fullPath: '/search/products',
          name: 'SearchProducts',
          path: '/',
        },
        $router: {push: mockPush},
      },
      stubs: ['router-link'],
    }))
    const field = wrapper.find('#nav-bar-search')
    await field.setValue('Stuff')
    await field.trigger('keyup')
    expect(mockPush).not.toHaveBeenCalled()
  })
})
