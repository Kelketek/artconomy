import {genArtistProfile, genUser} from '@/specs/helpers/fixtures.ts'
import {cleanUp, flushPromises, genAnon, mount, rs, vueSetup} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import mockAxios from '@/specs/helpers/mock-axios.ts'
import SubjectiveComponent from '@/specs/helpers/dummy_components/subjective-component.vue'
import {ProfileController} from '@/store/profiles/controller.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {setViewer} from '@/lib/lib.ts'

const localVue = vueSetup()

describe('Profile controller', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    mockAxios.reset()
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Updates the route if the username changed', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = vi.fn()
    wrapper = mount(Empty, {
      ...vueSetup({
        store,
        mocks: {
          $router: {
            replace,
            currentRoute: {name: 'Place', params: {username: 'Fox'}, query: {stuff: 'things'}, hash: 'Wheee'}
          },
        },
      }),
    })
    const controller = wrapper.vm.$getProfile('Fox', {})
    await wrapper.vm.$nextTick();
    controller.user.updateX({username: 'Vulpes_Veritas'})
    await wrapper.vm.$nextTick()
    expect(replace).toHaveBeenCalled()
    expect(replace).toHaveBeenCalledWith({
      name: 'Place', params: {username: 'Vulpes_Veritas'}, query: {stuff: 'things'}, hash: 'Wheee',
    },
    )
    // Should update the viewer name as well.
    expect((store.state as any).profiles.viewerRawUsername).toBe('Vulpes_Veritas')
  })
  test('Does not mess with the route if the username is unrelated', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = vi.fn()
    wrapper = mount(Empty, {
      ...vueSetup({
        store,
        mocks: {
          $router: {
            replace,
            currentRoute: {name: 'Place', params: {username: 'Fennec'}, query: {stuff: 'things'}, hash: 'Wheee'},
          },
        },
      }),
    })
    const controller = wrapper.vm.$getProfile('Arctic', {})
    await wrapper.vm.$nextTick()
    const arctic = genUser()
    arctic.username = 'Arctic';
    controller.user.setX(arctic)
    await wrapper.vm.$nextTick();
    controller.user.updateX({username: 'Vulpes_Veritas'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
    // No change to the viewer, so don't update the viewer name.
    expect((store.state as any).profiles.viewerRawUsername).toBe('Fox')
  })
  test('Does not mess with the route if there is no username param.', async() => {
    setViewer(store, genUser())
    const replace = vi.fn()
    wrapper = mount(Empty, {
      ...vueSetup({
        store,
        mocks: {
          $router: {
            replace,
            currentRoute: {name: 'Place', params: {wat: 'Do'}, query: {stuff: 'things'}, hash: 'Wheee'}
          },
        },
      })
    });
    const controller = wrapper.vm.$getProfile('Fox', {})
    controller.user.updateX({username: 'Vulpes_Veritas'})
    await wrapper.vm.$nextTick()
    // Doesn't automatically change the subjective user. The router will do this in the real world.
    // Thus, this should become null.
    expect(replace).toHaveBeenCalledTimes(0)
  })
  test('Does not mess with the route if the username has not changed.', async() => {
    setViewer(store, genUser())
    const replace = vi.fn()
    wrapper = mount(SubjectiveComponent, {
      ...vueSetup({
        store,
        mocks: {
          $router: {
            replace,
            currentRoute: {name: 'Place', params: {wat: 'Do'}, query: {stuff: 'things'}, hash: 'Wheee'}
          },
        },
      }),
      props: {username: 'Fox'},
    })
    wrapper.vm.subjectHandler.user.updateX({username: 'Fox', email: 'test@example.com'})
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).subject.username).toBe('Fox')
    expect((wrapper.vm as any).subject.email).toBe('test@example.com')
    expect(replace).toHaveBeenCalledTimes(0)
  })
  test('Migrates subcomponents if migrated', () => {
    const controller = mount(Empty, vueSetup({store})).vm.$getProfile('Fox', {})
    expect((store.state as any).userModules.goof).toBeFalsy()
    expect((store.state as any).userModules.Fox).toBeTruthy()
    expect((store.state as any).userModules.Fox.user).toBeTruthy()
    controller.migrate('goof')
    expect((store.state as any).userModules.goof).toBeTruthy()
    expect((store.state as any).userModules.goof.user).toBeTruthy()
    expect((store.state as any).userModules.Fox).toBeFalsy()
    // Shouldn't change things.
    controller.migrate('goof')
    expect((store.state as any).userModules.goof).toBeTruthy()
    expect((store.state as any).userModules.goof.user).toBeTruthy()
    expect((store.state as any).userModules.Fox).toBeFalsy()
  })
  test('Refreshes user data to an anonymous user', async() => {
    setViewer(store, genUser())
    const controller = mount(Empty, vueSetup({store})).vm.$getProfile('Fox', {}) as ProfileController
    controller.artistProfile.setX(genArtistProfile())
    controller.artistProfile.fetching = false
    controller.artistProfile.ready = true
    controller.refresh().then(() => {
      expect(controller.user.endpoint).toBe('/api/profiles/data/requester/')
      expect(controller.artistProfile.x).toBeNull()
    })
    mockAxios.mockResponse(rs(genAnon()))
    await flushPromises()
  })
  test('Refreshes user data to a registered user', async() => {
    const controller = mount(Empty, vueSetup({store})).vm.$getProfile('Fox', {})
    const profile = genArtistProfile()
    profile.auto_withdraw = false
    controller.artistProfile.setX(genArtistProfile())
    controller.artistProfile.fetching = false
    controller.artistProfile.ready = true
    controller.refresh().then()
    const user = genUser()
    user.username = 'Vulpes'
    mockAxios.mockResponse(rs(user))
    await flushPromises()
    expect(controller.user.endpoint).toBe('/api/profiles/account/Vulpes/')
    expect(controller.artistProfile.x).not.toBeNull()
    mockAxios.mockResponse(rs(genArtistProfile()))
    await flushPromises()
    expect(controller.artistProfile.x).not.toBeNull()
  })
})
