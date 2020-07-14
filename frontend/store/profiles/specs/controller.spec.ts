import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'
import {flushPromises, genAnon, rs, setViewer, vueSetup} from '@/specs/helpers'
import {mount, shallowMount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import Vue from 'vue'
import mockAxios from '@/specs/helpers/mock-axios'
import {singleRegistry} from '@/store/singles/registry'
import {profileRegistry} from '@/store/profiles/registry'
import SubjectiveComponent from '@/specs/helpers/dummy_components/subjective-component.vue'
import {ProfileController} from '@/store/profiles/controller'
import {getCookie} from '@/lib/lib'

const localVue = vueSetup()

describe('Profile controller', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue> | null
  beforeEach(() => {
    mockAxios.reset()
    singleRegistry.reset()
    profileRegistry.reset()
    store = createStore()
    wrapper = null
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Updates the route if the username changed', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = jest.fn()
    wrapper = mount(ProfileController, {
      localVue,
      store,
      propsData: {initName: 'Fox', schema: {}},
      mocks: {
        $route: {name: 'Place', params: {username: 'Fox'}, query: {stuff: 'things'}, hash: 'Wheee'},
        $router: {replace},
      },

    })
    await wrapper.vm.$nextTick();
    (wrapper.vm as any).user.updateX({username: 'Vulpes_Veritas'})
    await wrapper.vm.$nextTick()
    expect(replace).toHaveBeenCalled()
    expect(replace).toHaveBeenCalledWith({
      name: 'Place', params: {username: 'Vulpes_Veritas'}, query: {stuff: 'things'}, hash: 'Wheee',
    },
    )
    // Should udpate the viewer name as well.
    expect((store.state as any).profiles.viewerRawUsername).toBe('Vulpes_Veritas')
  })
  it('Does not mess with the route if the username is unrelated', async() => {
    const user = genUser()
    setViewer(store, user)
    const replace = jest.fn()
    wrapper = mount(ProfileController, {
      localVue,
      store,
      propsData: {initName: 'Arctic', schema: {}},
      mocks: {
        $route: {name: 'Place', params: {username: 'Fennec'}, query: {stuff: 'things'}, hash: 'Wheee'},
        $router: {replace},
      },

    })
    await wrapper.vm.$nextTick()
    const arctic = genUser()
    arctic.username = 'Arctic';
    (wrapper.vm as any).user.setX(arctic)
    await wrapper.vm.$nextTick();
    (wrapper.vm as any).user.updateX({username: 'Vulpes_Veritas'})
    await wrapper.vm.$nextTick()
    expect(replace).not.toHaveBeenCalled()
    // No change to the viewer, so don't update the viewer name.
    expect((store.state as any).profiles.viewerRawUsername).toBe('Fox')
  })
  it('Does not mess with the route if there is no username param.', async() => {
    setViewer(store, genUser())
    const replace = jest.fn()
    wrapper = mount(ProfileController, {
      localVue,
      store,
      propsData: {initName: 'Fox', schema: {}},
      mocks: {
        $route: {name: 'Place', params: {wat: 'Do'}, query: {stuff: 'things'}, hash: 'Wheee'},
        $router: {replace},
      },

    });
    (wrapper.vm as any).user.updateX({username: 'Vulpes_Veritas'})
    await wrapper.vm.$nextTick()
    // Doesn't automatically change the subjective user. The router will do this in the real world.
    // Thus, this should become null.
    expect(replace).toHaveBeenCalledTimes(0)
  })
  it('Does not mess with the route if the username has not changed.', async() => {
    setViewer(store, genUser())
    const replace = jest.fn()
    wrapper = shallowMount(SubjectiveComponent, {
      localVue,
      store,
      propsData: {username: 'Fox'},
      mocks: {
        $route: {name: 'Place', params: {wat: 'Do'}, query: {stuff: 'things'}, hash: 'Wheee'},
        $router: {replace},
      },

    });
    (wrapper.vm as any).subjectHandler.user.updateX({username: 'Fox', email: 'test@example.com'})
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).subject.username).toBe('Fox')
    expect((wrapper.vm as any).subject.email).toBe('test@example.com')
    expect(replace).toHaveBeenCalledTimes(0)
  })
  it('Migrates subcomponents if migrated', () => {
    const controller = mount(ProfileController, {
      localVue,
      store,
      propsData: {initName: 'Fox', schema: {}},

    }).vm as ProfileController
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
  it('Updates authentication tokens', async() => {
    setViewer(store, genUser())
    const user = genUser()
    user.csrftoken = 'Hello!'
    user.authtoken = 'Howdy!'
    const controller = mount(ProfileController, {
      localVue,
      store,
      propsData: {initName: 'Fox', schema: {}},

    }).vm as ProfileController
    controller.user.setX(user)
    await controller.$nextTick()
    expect(getCookie('csrftoken')).toBe('Hello!')
    expect(getCookie('authtoken')).toBe('Howdy!')
  })
  it('Refreshes user data to an anonymous user', async() => {
    setViewer(store, genUser())
    const controller = mount(ProfileController, {
      localVue,
      store,
      propsData: {initName: 'Fox', schema: {}},

    }).vm as ProfileController
    controller.artistProfile.setX(genArtistProfile())
    controller.artistProfile.fetching = false
    controller.artistProfile.ready = true
    controller.refresh().then(() => {
      expect(controller.user.endpoint).toBe('/api/profiles/v1/data/requester/')
      expect(controller.artistProfile.x).toBeNull()
    })
    mockAxios.mockResponse(rs(genAnon()))
    await flushPromises()
  })
  it('Refreshes user data to a registered user', async() => {
    const controller = mount(ProfileController, {
      localVue,
      store,
      propsData: {initName: 'Fox', schema: {}},

    }).vm as ProfileController
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
    expect(controller.user.endpoint).toBe('/api/profiles/v1/account/Vulpes/')
    expect(controller.artistProfile.x).not.toBeNull()
    mockAxios.mockResponse(rs(genArtistProfile()))
    await flushPromises()
    expect(controller.artistProfile.x).not.toBeNull()
  })
})
