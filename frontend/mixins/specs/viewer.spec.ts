import {createLocalVue, shallowMount, Wrapper} from '@vue/test-utils'
import mockAxios from '@/specs/helpers/mock-axios'
import {genUser} from '@/specs/helpers/fixtures'
import {ArtStore, createStore} from '@/store'
import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import {docTarget, genAnon, mount, setViewer} from '@/specs/helpers'
import {Ratings} from '@/store/profiles/types/Ratings'
import ViewerComponent from '@/specs/helpers/dummy_components/viewer.vue'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {Lists} from '@/store/lists/registry'
import SearchProducts from '@/components/views/search/SearchProducts.vue'

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
    setViewer(store, user)
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).rating).toBe(Ratings.EXTREME)
  })
  it('Lowers the rating on SFW mode', async() => {
    const user = genUser()
    user.rating = Ratings.EXTREME
    user.sfw_mode = true
    setViewer(store, user)
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const rating = store.getters['profiles/rating']
    expect((wrapper.vm as any).rating).toBe(Ratings.GENERAL)
  })
  it('Sets the rating to general if not logged in', async() => {
    setViewer(store, genAnon())
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).rating).toBe(Ratings.GENERAL)
  })
  it('Considers adult content "off" if sfw mode is on', async() => {
    setViewer(store, genUser({rating: Ratings.ADULT, sfw_mode: true}))
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).adultAllowed).toBe(false)
  })
  it('Considers adult content "on" if sfw mode is off and rating is high enough', async() => {
    setViewer(store, genUser({rating: Ratings.ADULT, sfw_mode: false}))
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).adultAllowed).toBe(true)
  })
  it('Reports the user as not logged if no viewer is set', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isLoggedIn).toBe(false)
  })
  it('Reports the user as logged in if a viewer is set', async() => {
    setViewer(store, genUser())
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isLoggedIn).toBe(true)
  })
  it('Reports the user as registered in if a viewer is set and not a guest', async() => {
    setViewer(store, genUser())
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isRegistered).toBe(true)
  })
  it('Reports the user as not registered if a guest.', async() => {
    const user = genUser()
    user.guest = true
    setViewer(store, user)
    wrapper = shallowMount(ViewerComponent, {localVue, store})
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
  it('Reports landscape status as false when viewer is anonymous', () => {
    setViewer(store, genAnon())
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).landscape).toBe(false)
  })
  it('Reports landscape status as false when viewer landscape is false', () => {
    const user = genUser()
    user.landscape = false
    setViewer(store, user)
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).landscape).toBe(false)
  })
  it('Reports landscape status as true when viewer landscape is true', () => {
    const user = genUser()
    user.landscape = true
    setViewer(store, user)
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).landscape).toBe(true)
  })
  it('Returns a guest username when the viewer is a guest.', () => {
    const user = genUser()
    user.guest = true
    user.id = 500
    setViewer(store, user)
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).viewerName).toBe('Guest #500')
  })
  it('Returns a blank username when the viewer is null.', () => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).viewerName).toBe('')
  })
  it('Returns a blank username when the viewer is not logged in.', () => {
    setViewer(store, genAnon())
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).viewerName).toBe('')
  })
  it('Identifies the user as a superuser if they are one', async() => {
    setViewer(store, genUser({is_superuser: true}))
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isSuperuser).toBe(true)
  })
  it('Identifies the user as not a superuser if they are not one', async() => {
    const user = genUser({is_superuser: false})
    user.is_superuser = false
    setViewer(store, user)
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isSuperuser).toBe(false)
  })
  it('Identifies the user as not a superuser if they are not logged in', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isSuperuser).toBe(false)
  })
  it('Identifies the user as a staffer if they are one', async() => {
    setViewer(store, genUser({is_staff: true}))
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isStaff).toBe(true)
  })
  it('Identifies the user as not a staffer if they are not one', async() => {
    const user = genUser({is_staff: false})
    user.is_staff = false
    setViewer(store, user)
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isStaff).toBe(false)
  })
  it('Identifies the user as not a staffer if they are not logged in', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).isStaff).toBe(false)
  })
  it('Returns a normal username when the viewer is not a guest and is logged in.', () => {
    const user = genUser()
    user.guest = false
    user.username = 'TestPerson'
    setViewer(store, user)
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    expect((wrapper.vm as any).viewerName).toBe('TestPerson')
  })
  it('Handles a known error status', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const vm = wrapper.vm as any
    // Should not throw.
    vm.statusOk(403)({response: {status: 403}})
    // Should throw.
    const error = {response: {status: 400}, name: 'TestError', message: 'Failed!'}
    expect(() => vm.statusOk(403)(error)).toThrow(error)
  })
  it('Prompts for age verification', async() => {
    setViewer(store, genAnon())
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const vm = wrapper.vm as any
    expect(store.state.ageAsked).toBe(false)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(0)
    vm.ageCheck({value: 2})
    await vm.$nextTick()
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(true)
    expect(store.state.contentRating).toBe(2)
  })
  it('Does not reprompt age verification', async() => {
    setViewer(store, genAnon())
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const vm = wrapper.vm as any
    vm.ageCheck({value: 2})
    await vm.$nextTick()
    store.commit('setShowAgeVerification', false)
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(2)
    vm.ageCheck({value: 3})
    await vm.$nextTick()
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(2)
  })
  it('Forces reprompting', async() => {
    setViewer(store, genAnon())
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const vm = wrapper.vm as any
    vm.ageCheck({value: 2})
    await vm.$nextTick()
    store.commit('setShowAgeVerification', false)
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(2)
    vm.ageCheck({value: 3, force: true})
    await vm.$nextTick()
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(true)
    expect(store.state.contentRating).toBe(3)
  })
  it('Skips if the viewer has set their birthday', async() => {
    setViewer(store, genUser())
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const vm = wrapper.vm as any
    vm.ageCheck({value: 2})
    await vm.$nextTick()
    expect(store.state.ageAsked).toBe(false)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(0)
  })
  it('Determines the derived rating', async() => {
    wrapper = shallowMount(ViewerComponent, {localVue, store})
    const vm = wrapper.vm as any
    expect(vm.rawRating).toBe(undefined)
    vm.viewerHandler.user.makeReady(genUser({rating: Ratings.GENERAL}))
    await vm.$nextTick()
    expect(vm.rawRating).toBe(Ratings.GENERAL)
    vm.viewerHandler.user.updateX({rating: Ratings.ADULT})
    await vm.$nextTick()
    expect(vm.rawRating).toBe(Ratings.ADULT)
    vm.viewerHandler.user.updateX({sfw_mode: true})
    await vm.$nextTick()
    expect(vm.rawRating).toBe(Ratings.GENERAL)
  })
})
