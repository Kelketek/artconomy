import {createLocalVue, shallowMount, Wrapper} from '@vue/test-utils'
import {genUser} from '@/specs/helpers/fixtures'
import {ArtStore, createStore} from '@/store'
import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import Router, {RouterMode} from 'vue-router'
import SubjectiveComponent from '@/specs/helpers/dummy_components/subjective-component.vue'
import {docTarget, setViewer} from '@/specs/helpers'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {Lists} from '@/store/lists/registry'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const mockError = jest.spyOn(console, 'error')

describe('Subjective.ts', () => {
  let store: ArtStore
  let vue: Vue
  let localVue: VueConstructor
  let wrapper: Wrapper<Vue> | null
  let router: Router
  beforeEach(() => {
    router = new Router({
      mode: 'history' as RouterMode,
      routes: [{
        path: '/',
        name: 'Login',
        component: Empty,
      }],
    })
    localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(Singles)
    localVue.use(Lists)
    localVue.use(Profiles)
    localVue.use(Router)
    singleRegistry.reset()
    profileRegistry.reset()
    store = createStore()
    mockError.mockReset()
    wrapper = null
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Fetches the subject', async() => {
    setViewer(store, genUser())
    wrapper = shallowMount(SubjectiveComponent, {localVue, store, router, propsData: {username: 'Fox'}})
    expect((wrapper.vm as any).username).toBe('Fox')
    expect((wrapper.vm as any).subjectHandler).toBeTruthy()
    expect((wrapper.vm as any).subject.username).toBe('Fox')
  })
  it('Updates the subject', async() => {
    setViewer(store, genUser())
    store.commit('profiles/saveUser', genUser())
    wrapper = shallowMount(
      SubjectiveComponent, {localVue, store, router, propsData: {username: 'Fox'}, attachTo: docTarget()},
    )
    expect((wrapper.vm as any).subject.email).toBe('fox@artconomy.com');
    (wrapper.vm as any).subjectHandler.user.updateX({email: 'test@example.com'})
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).subject.username).toBe('Fox')
    expect((wrapper.vm as any).subject.email).toBe('test@example.com')
  })
  it('Changes the current viewer username if they are the subject.', async() => {
    setViewer(store, genUser())
    store.commit('profiles/setViewerUsername', 'Fox')
    wrapper = shallowMount(SubjectiveComponent, {
      localVue,
      store,
      router,
      propsData: {username: 'Fox'},
      mocks: {
        $route: {name: 'Place', params: {}, query: {}, hash: ''},
      },
    });
    (wrapper.vm as any).subjectHandler.user.updateX({username: 'Vulpes_Veritas'})
    await wrapper.vm.$nextTick()
    expect((store.state as any).profiles.viewerRawUsername).toBe('Vulpes_Veritas')
  })
  it('Allows the user to see if they are the subject and the view is private', async() => {
    expect((store.state as any).errors.code).toBe(0)
    const user = genUser()
    user.is_staff = false
    user.is_superuser = false
    setViewer(store, user)
    wrapper = shallowMount(SubjectiveComponent, {
      localVue,
      store,
      router,
      propsData: {username: 'Fox'},
      data() {
        return {privateView: true}
      },
      mocks: {
        $route: {name: 'Place', params: {}, query: {}, hash: ''},
      },
    })
    await wrapper.vm.$nextTick()
    expect((store.state as any).errors.code).toBe(0)
  })
  it('Sends the user to an error if they are not the subject and the view is private', async() => {
    setViewer(store, genUser())
    expect((store.state as any).errors.code).toBe(0)
    wrapper = shallowMount(SubjectiveComponent, {
      localVue,
      store,
      router,
      propsData: {username: 'Vulpes'},
      data() {
        return {privateView: true}
      },
      mocks: {
        $route: {name: 'Place', params: {}, query: {}, hash: ''},
      },
    })
    await wrapper.vm.$nextTick()
    expect((store.state as any).errors.code).toBe(403)
  })
  it('Redirects the user to login if they are not logged in and the view is private', async() => {
    expect((store.state as any).errors.code).toBe(0)
    wrapper = shallowMount(SubjectiveComponent, {
      localVue,
      store,
      router,
      propsData: {username: 'Vulpes'},
      data() {
        return {privateView: true}
      },
      mocks: {
        $route: {name: 'Place', params: {}, query: {}, hash: ''},
      },
    })
    await wrapper.vm.$nextTick()
    expect((store.state as any).errors.code).toBe(0)
    expect(wrapper.vm.$route.name).toBe('Login')
  })
  it('Allows the user to see if they are not the subject and the view is private but they are a staffer',
    async() => {
      expect((store.state as any).errors.code).toBe(0)
      const user = genUser()
      user.is_superuser = false
      user.is_staff = true
      setViewer(store, user)
      wrapper = shallowMount(SubjectiveComponent, {
        localVue,
        store,
        router,
        propsData: {username: 'Vulpes'},
        data() {
          return {privateView: true}
        },
        mocks: {
          $route: {name: 'Place', params: {}, query: {}, hash: ''},
        },
      })
      await wrapper.vm.$nextTick()
      expect((store.state as any).errors.code).toBe(0)
    })
  it('Does not permit a normal staffer to access a protected view',
    async() => {
      expect((store.state as any).errors.code).toBe(0)
      const user = genUser()
      user.is_superuser = false
      user.is_staff = true
      setViewer(store, user)
      wrapper = shallowMount(SubjectiveComponent, {
        localVue,
        store,
        router,
        propsData: {username: 'Vulpes'},
        data() {
          return {protectedView: true, privateView: true}
        },
        mocks: {
          $route: {name: 'Place', params: {}, query: {}, hash: ''},
        },
      })
      await wrapper.vm.$nextTick()
      expect((store.state as any).errors.code).toBe(403)
    })
  it('Allows a superuser to access a protected view',
    async() => {
      expect((store.state as any).errors.code).toBe(0)
      const user = genUser()
      user.is_superuser = true
      user.is_staff = true
      setViewer(store, user)
      wrapper = shallowMount(SubjectiveComponent, {
        localVue,
        store,
        router,
        propsData: {username: 'Fox'},
        data() {
          return {protectedView: true, privateView: true}
        },
        mocks: {
          $route: {name: 'Place', params: {}, query: {}, hash: ''},
        },
      })
      await wrapper.vm.$nextTick()
      expect((store.state as any).errors.code).toBe(0)
    })
})
