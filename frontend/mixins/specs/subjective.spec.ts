import {createLocalVue, shallowMount, Wrapper} from '@vue/test-utils'
import {genUser} from '@/specs/helpers/fixtures'
import {ArtStore, createStore} from '@/store'
import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import SubjectiveComponent from '@/specs/helpers/dummy_components/subjective-component.vue'
import {setViewer} from '@/specs/helpers'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {Lists} from '@/store/lists/registry'

const mockError = jest.spyOn(console, 'error')

describe('Subjective.ts', () => {
  let store: ArtStore
  let vue: Vue
  let localVue: VueConstructor
  let wrapper: Wrapper<Vue> | null
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(Singles)
    localVue.use(Lists)
    localVue.use(Profiles)
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
    wrapper = shallowMount(SubjectiveComponent, {localVue, store, propsData: {username: 'Fox'}, sync: false})
    expect((wrapper.vm as any).username).toBe('Fox')
    expect((wrapper.vm as any).subjectHandler).toBeTruthy()
    expect((wrapper.vm as any).subject.username).toBe('Fox')
  })
  it('Updates the subject', async() => {
    setViewer(store, genUser())
    store.commit('profiles/saveUser', genUser())
    wrapper = shallowMount(
      SubjectiveComponent, {localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true}
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
      propsData: {username: 'Fox'},
      mocks: {
        $route: {name: 'Place', params: {}, query: {}, hash: ''},
      },
      sync: false,
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
      propsData: {username: 'Fox'},
      data() {
        return {privateView: true}
      },
      mocks: {
        $route: {name: 'Place', params: {}, query: {}, hash: ''},
      },
      sync: false,
    })
    await wrapper.vm.$nextTick()
    expect((store.state as any).errors.code).toBe(0)
  })
  it('Sends the user to an error if they are not the subject and the view is private', async() => {
    expect((store.state as any).errors.code).toBe(0)
    wrapper = shallowMount(SubjectiveComponent, {
      localVue,
      store,
      propsData: {username: 'Vulpes'},
      data() {
        return {privateView: true}
      },
      mocks: {
        $route: {name: 'Place', params: {}, query: {}, hash: ''},
      },
      sync: false,
    })
    await wrapper.vm.$nextTick()
    expect((store.state as any).errors.code).toBe(403)
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
        propsData: {username: 'Vulpes'},
        data() {
          return {privateView: true}
        },
        mocks: {
          $route: {name: 'Place', params: {}, query: {}, hash: ''},
        },
        sync: false,
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
        propsData: {username: 'Vulpes'},
        data() {
          return {protectedView: true, privateView: true}
        },
        mocks: {
          $route: {name: 'Place', params: {}, query: {}, hash: ''},
        },
        sync: false,
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
        propsData: {username: 'Fox'},
        data() {
          return {protectedView: true, privateView: true}
        },
        mocks: {
          $route: {name: 'Place', params: {}, query: {}, hash: ''},
        },
        sync: false,
      })
      await wrapper.vm.$nextTick()
      expect((store.state as any).errors.code).toBe(0)
    })
})
