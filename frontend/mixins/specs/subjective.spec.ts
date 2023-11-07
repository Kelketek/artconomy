import {mount, VueWrapper} from '@vue/test-utils'
import {genUser} from '@/specs/helpers/fixtures'
import {ArtStore, createStore} from '@/store'
import {createRouter, createWebHistory, Router} from 'vue-router'
import SubjectiveComponent from '@/specs/helpers/dummy_components/subjective-component.vue'
import {cleanUp, docTarget, setViewer, vueSetup} from '@/specs/helpers'
import Empty from '@/specs/helpers/dummy_components/empty'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

const mockError = vi.spyOn(console, 'error')

describe('Subjective.ts', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  let router: Router
  beforeEach(() => {
    router = createRouter({
      history: createWebHistory(),
      routes: [{
        path: '/',
        name: 'Login',
        component: Empty,
      }, {
        path: '/place',
        name: 'Place',
        component: Empty,
      }],
    })
    store = createStore()
    mockError.mockReset()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Fetches the subject', async() => {
    setViewer(store, genUser())
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {username: 'Fox'},
    })
    expect((wrapper.vm as any).username).toBe('Fox')
    expect((wrapper.vm as any).subjectHandler).toBeTruthy()
    expect((wrapper.vm as any).subject.username).toBe('Fox')
  })
  test('Updates the subject', async() => {
    setViewer(store, genUser())
    store.commit('profiles/saveUser', genUser())
    wrapper = mount(
      SubjectiveComponent, {
        ...vueSetup({
          store,
          extraPlugins: [router],
        }),
        props: {username: 'Fox'},
        attachTo: docTarget(),
      },
    )
    expect((wrapper.vm as any).subject.email).toBe('fox@artconomy.com');
    (wrapper.vm as any).subjectHandler.user.updateX({email: 'test@example.com'})
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).subject.username).toBe('Fox')
    expect((wrapper.vm as any).subject.email).toBe('test@example.com')
  })
  test('Changes the current viewer username if they are the subject.', async() => {
    setViewer(store, genUser())
    store.commit('profiles/setViewerUsername', 'Fox')
    wrapper = mount(SubjectiveComponent, {...vueSetup({
      store,
      extraPlugins: [router],
      mocks: {
        $route: {
          name: 'Place',
          params: {},
          query: {},
          hash: '',
        },
      },
    }),
      props: {username: 'Fox'},
    });
    (wrapper.vm as any).subjectHandler.user.updateX({username: 'Vulpes_Veritas'})
    await wrapper.vm.$nextTick()
    expect((store.state as any).profiles.viewerRawUsername).toBe('Vulpes_Veritas')
  })
  test('Allows the user to see if they are the subject and the view is private', async() => {
    expect((store.state as any).errors.code).toBe(0)
    const user = genUser()
    user.is_staff = false
    user.is_superuser = false
    setViewer(store, user)
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        mocks: {
          $route: {
            name: 'Place',
            params: {},
            query: {},
            hash: '',
          },
        },
      }),
      data() {
        return {privateView: true}
      },
      props: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
    expect((store.state as any).errors.code).toBe(0)
  })
  test('Sends the user to an error if they are not the subject and the view is private', async() => {
    setViewer(store, genUser())
    expect((store.state as any).errors.code).toBe(0)
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        mocks: {
          $route: {
            name: 'Place',
            params: {},
            query: {},
            hash: '',
          },
        },
      }),
      props: {username: 'Vulpes'},
      data() {
        return {privateView: true}
      },
    })
    await wrapper.vm.$nextTick()
    expect((store.state as any).errors.code).toBe(403)
  })
  test('Redirects the user to login if they are not logged in and the view is private', async() => {
    expect((store.state as any).errors.code).toBe(0)
    await router.replace({name: 'Place'})
    await router.isReady()
    const replace = vi.fn()
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        mocks: {
          $route: {name: 'Place', params: {}, query: {}, hash: '', fullPath: '/place'},
          $router: {replace}
        },
      }),
      props: {username: 'Vulpes'},
      data() {
        return {privateView: true}
      },
    })
    expect((store.state as any).errors.code).toBe(0)
    expect(replace).toHaveBeenCalledWith({name: 'Login', query: {next: '/place'}})
  })
  test('Allows the user to see if they are not the subject and the view is private but they are a staffer',
    async() => {
      expect((store.state as any).errors.code).toBe(0)
      const user = genUser()
      user.is_superuser = false
      user.is_staff = true
      setViewer(store, user)
      wrapper = mount(SubjectiveComponent, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          mocks: {
            $route: {
              name: 'Place',
              params: {},
              query: {},
              hash: '',
            },
          },
        }),
        props: {username: 'Vulpes'},
        data() {
          return {privateView: true}
        },
      })
      await wrapper.vm.$nextTick()
      expect((store.state as any).errors.code).toBe(0)
    })
  test('Does not permit a normal staffer to access a protected view',
    async() => {
      expect((store.state as any).errors.code).toBe(0)
      const user = genUser()
      user.is_superuser = false
      user.is_staff = true
      setViewer(store, user)
      wrapper = mount(SubjectiveComponent, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          mocks: {
            $route: {
              name: 'Place',
              params: {},
              query: {},
              hash: '',
            },
          },
        }),
        props: {username: 'Vulpes'},
        data() {
          return {
            protectedView: true,
            privateView: true,
          }
        },
      })
      await wrapper.vm.$nextTick()
      expect((store.state as any).errors.code).toBe(403)
    })
  test('Allows a superuser to access a protected view',
    async() => {
      expect((store.state as any).errors.code).toBe(0)
      const user = genUser()
      user.is_superuser = true
      user.is_staff = true
      setViewer(store, user)
      wrapper = mount(SubjectiveComponent, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          mocks: {
            $route: {
              name: 'Place',
              params: {},
              query: {},
              hash: '',
            },
          },
        }),
        props: {username: 'Fox'},
        data() {
          return {
            protectedView: true,
            privateView: true,
          }
        },
      })
      await wrapper.vm.$nextTick()
      expect((store.state as any).errors.code).toBe(0)
    })
})
