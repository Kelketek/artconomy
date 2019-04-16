import {createLocalVue, mount, shallowMount, Wrapper} from '@vue/test-utils'
import mockAxios from '@/specs/helpers/mock-axios'
import {genUser} from '@/specs/helpers/fixtures'
import {ArtStore, createStore} from '@/store'
import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import {flushPromises, genAnon, rq, rs} from '@/specs/helpers'
import {Ratings} from '@/store/profiles/types/Ratings'
import ViewerComponent from '@/specs/helpers/dummy_components/viewer.vue'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {getCookie} from '@/lib'
import {Lists} from '@/store/lists/registry'

describe('Viewer.ts', () => {
  let store: ArtStore
  let localVue: VueConstructor
  let wrapper: Wrapper<Vue> | null
  beforeEach(() => {
    mockAxios.reset()
    singleRegistry.reset()
    profileRegistry.reset()
    localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(Singles)
    localVue.use(Lists)
    localVue.use(Profiles)
    store = createStore()
    if (wrapper) {
      wrapper.destroy()
    }
    wrapper = null
  })
  it('Returns the correct rating for the viewer', async() => {
    const user = genUser()
    user.rating = Ratings.EXTREME
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).rating).toBe(Ratings.EXTREME)
  })
  it('Lowers the rating on SFW mode', async() => {
    const user = genUser()
    user.rating = Ratings.EXTREME
    user.sfw_mode = true
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(user))
    const rating = store.getters['profiles/rating']
    expect((wrapper.vm as any).rating).toBe(Ratings.GENERAL)
  })
  it('Sets the rating to general if not logged in', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(genAnon()))
    expect((wrapper.vm as any).rating).toBe(Ratings.GENERAL)
  })
  it('Reports the user as not logged if no viewer is set', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isLoggedIn).toBe(false)
  })
  it('Reports the user as logged in if a viewer is set', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(genUser()))
    expect((wrapper.vm as any).isLoggedIn).toBe(true)
  })
  it('Reports the user as registered in if a viewer is set and not a guest', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(genUser()))
    expect((wrapper.vm as any).isRegistered).toBe(true)
  })
  it('Reports the user as not registered if a guest.', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const user = genUser()
    user.guest = true
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).isRegistered).toBe(false)
  })
  it('Reports the user as not registerd if not set.', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isRegistered).toBe(false)
  })
  it('Reports landscape status as false when viewer is null', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).landscape).toBe(false)
  })
  it('Reports landscape status as false when viewer is empty', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(genAnon()))
    expect((wrapper.vm as any).landscape).toBe(false)
  })
  it('Reports landscape status as false when viewer landscape is false', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const user = genUser()
    user.landscape = false
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).landscape).toBe(false)
  })
  it('Reports landscape status as true when viewer landscape is true', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const user = genUser()
    user.landscape = true
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).landscape).toBe(true)
  })
  it('Reports portrait status as false when viewer is null', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).portrait).toBe(false)
  })
  it('Reports portrait status as false when viewer is empty', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(genAnon()))
    expect((wrapper.vm as any).portrait).toBe(false)
  })
  it('Reports portrait status as false when viewer portrait is false', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const user = genUser()
    user.portrait = false
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).portrait).toBe(false)
  })
  it('Reports portrait status as true when viewer portrait is true', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const user = genUser()
    user.portrait = true
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).portrait).toBe(true)
  })
  it('Returns a guest username when the viewer is a guest.', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const user = genUser()
    user.guest = true
    user.id = 500
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).viewerName).toBe('Guest #500')
  })
  it('Returns a blank username when the viewer is null.', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).viewerName).toBe('')
  })
  it('Returns a blank username when the viewer is not logged in.', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(genAnon()))
    expect((wrapper.vm as any).viewerName).toBe('')
  })
  it('Identifies the user as a superuser if they are one', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(genUser()))
    expect((wrapper.vm as any).isSuperuser).toBe(true)
  })
  it('Identifies the user as not a superuser if they are not one', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const user = genUser()
    user.is_superuser = false
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).isSuperuser).toBe(false)
  })
  it('Identifies the user as not a superuser if they are not logged in', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isSuperuser).toBe(false)
  })
  it('Identifies the user as a staffer if they are one', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    mockAxios.mockResponse(rs(genUser()))
    expect((wrapper.vm as any).isStaff).toBe(true)
  })
  it('Identifies the user as not a staffer if they are not one', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const user = genUser()
    user.is_staff = false
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).isStaff).toBe(false)
  })
  it('Identifies the user as not a staffer if they are not logged in', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isStaff).toBe(false)
  })
  it('Returns a normal username when the viewer is not a guest and is logged in.', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const user = genUser()
    user.guest = false
    user.username = 'TestPerson'
    mockAxios.mockResponse(rs(user))
    expect((wrapper.vm as any).viewerName).toBe('TestPerson')
  })
})
