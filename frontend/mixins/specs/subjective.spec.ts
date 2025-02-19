import {mount, VueWrapper} from '@vue/test-utils'
import {genPowers, genUser} from '@/specs/helpers/fixtures.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {createRouter, createWebHistory, Router} from 'vue-router'
import SubjectiveComponent from '@/specs/helpers/dummy_components/subjective-component.vue'
import {cleanUp, vueSetup, waitFor} from '@/specs/helpers/index.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import {nextTick} from 'vue'
import {StaffPower} from '@/store/profiles/types/main'

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
    setViewer({ store, user: genUser() })
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        router,
      }),
      props: {username: 'Fox'},
    })
    expect(wrapper.vm.username).toBe('Fox')
    expect(wrapper.vm.subjectHandler).toBeTruthy()
    expect(wrapper.vm.subject.username).toBe('Fox')
  })
  test('Updates the subject', async() => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      SubjectiveComponent, {
        ...vueSetup({
          store,
          router,
        }),
        props: {username: 'Fox'},
      },
    )
    expect(wrapper.vm.subject.email).toBe('fox@artconomy.com')
    wrapper.vm.subjectHandler.user.updateX({email: 'test@example.com'})
    await nextTick()
    expect(wrapper.vm.subject.username).toBe('Fox')
    expect(wrapper.vm.subject.email).toBe('test@example.com')
  })
  test('Changes the current viewer username if they are the subject.', async() => {
    setViewer({ store, user: genUser() })
    store.commit('profiles/setViewerUsername', 'Fox')
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        router,
      }),
      props: {username: 'Fox'},
    })
    wrapper.vm.subjectHandler.user.updateX({username: 'Vulpes_Veritas'})
    await nextTick()
    expect((store.state as any).profiles.viewerRawUsername).toBe('Vulpes_Veritas')
  })
  test('Allows the user to see if they are the subject and the view is private', async() => {
    expect((store.state as any).errors.code).toBe(0)
    await router.push('/place')
    const user = genUser()
    user.is_staff = false
    user.is_superuser = false
    setViewer({ store, user })
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        username: 'Fox',
        isPrivate: true,
      },
    })
    await nextTick()
    expect(store.state.errors!.code).toBe(0)
  })
  test('Sends the user to an error if they are not the subject and the view is private', async() => {
    await router.push('/place')
    setViewer({ store, user: genUser() })
    expect(store.state.errors!.code).toBe(0)
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        username: 'Vulpes',
        isPrivate: true,
      },
    })
    await nextTick()
    expect(store.state.errors!.code).toBe(403)
  })
  test('Redirects the user to login if they are not logged in and the view is private', async() => {
    expect((store.state as any).errors.code).toBe(0)
    await router.push({name: 'Place'})
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        username: 'Vulpes',
        isPrivate: true,
      },
    })
    expect(store.state.errors!.code).toBe(0)
    await waitFor(() => expect(router.currentRoute.value.name).toBe('Login'))
    expect(router.currentRoute.value.query).toEqual({next: '/place'})
  })
  test('Allows the user to see if they are not the subject and the view is private but they are a staffer with the right powers',
    async() => {
      await router.push('/place')
      expect((store.state as any).errors.code).toBe(0)
      const user = genUser()
      user.is_superuser = false
      user.is_staff = true
      setViewer({ store, user, powers: genPowers({administrate_users: true})})
      wrapper = mount(SubjectiveComponent, {
        ...vueSetup({
          store,
          router,
        }),
        props: {
          username: 'Vulpes',
          isPrivate: true,
          hasControlPowers: ['administrate_users'] as StaffPower[],
        },
      })
      await nextTick()
      expect(store.state.errors!.code).toBe(0)
    })
  test('Does not permit an unqualified staffer to access a protected view',
    async() => {
      expect((store.state as any).errors.code).toBe(0)
      const user = genUser()
      user.is_superuser = false
      user.is_staff = true
      setViewer({ store, user, powers: genPowers() })
      wrapper = mount(SubjectiveComponent, {
        ...vueSetup({
          store,
          router,
        }),
        props: {
          username: 'Vulpes',
          isPrivate: true,
          hasControlPowers: ['administrate_users'] as StaffPower[],
        },
      })
      await nextTick()
      expect((store.state as any).errors.code).toBe(403)
    })
  test('Allows a superuser to access a protected view',
    async() => {
      await router.push('/place')
      expect(store.state.errors!.code).toBe(0)
      const user = genUser()
      user.is_superuser = true
      user.is_staff = true
      setViewer({ store, user })
      wrapper = mount(SubjectiveComponent, {
        ...vueSetup({
          store,
        }),
        props: {
          username: 'Fox',
          isProtected: true,
          isPrivate: true,
        },
      })
      await nextTick()
      expect(store.state.errors!.code).toBe(0)
    })
})
