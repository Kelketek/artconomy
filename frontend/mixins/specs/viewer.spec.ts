import { genAnon, genUser } from "@/specs/helpers/fixtures.ts"
import { ArtStore, createStore } from "@/store/index.ts"
import { cleanUp, mount, vueSetup } from "@/specs/helpers/index.ts"
import { Ratings } from "@/types/enums/Ratings.ts"
import ViewerComponent from "@/specs/helpers/dummy_components/viewer.vue"
import { afterEach, beforeEach, describe, expect, test } from "vitest"
import { VueWrapper } from "@vue/test-utils"
import { setViewer } from "@/lib/lib.ts"
import { nextTick } from "vue"

describe("Viewer.ts", () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Returns the correct rating for the viewer", async () => {
    const user = genUser()
    user.rating = Ratings.EXTREME
    setViewer({ store, user })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.rating).toBe(Ratings.EXTREME)
  })
  test("Lowers the rating on SFW mode", async () => {
    const user = genUser()
    user.rating = Ratings.EXTREME
    user.sfw_mode = true
    setViewer({ store, user })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.rating).toBe(Ratings.GENERAL)
  })
  test("Sets the rating to general if not logged in", async () => {
    setViewer({ store, user: genAnon() })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.rating).toBe(Ratings.GENERAL)
  })
  test('Considers adult content "off" if sfw mode is on', async () => {
    setViewer({
      store,
      user: genUser({ rating: Ratings.ADULT, sfw_mode: true }),
    })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.adultAllowed).toBe(false)
  })
  test('Considers adult content "on" if sfw mode is off and rating is high enough', async () => {
    setViewer({
      store,
      user: genUser({ rating: Ratings.ADULT, sfw_mode: false }),
    })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.adultAllowed).toBe(true)
  })
  test("Reports the user as not logged if no viewer is set", async () => {
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isLoggedIn).toBe(false)
  })
  test("Reports the user as logged in if a viewer is set", async () => {
    setViewer({ store, user: genUser() })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isLoggedIn).toBe(true)
  })
  test("Reports the user as registered in if a viewer is set and not a guest", async () => {
    setViewer({ store, user: genUser() })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isRegistered).toBe(true)
  })
  test("Reports the user as not registered if a guest.", async () => {
    const user = genUser()
    user.guest = true
    setViewer({ store, user })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isRegistered).toBe(false)
  })
  test("Reports the user as not registerd if not set.", async () => {
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isRegistered).toBe(false)
  })
  test("Reports landscape status as false when viewer is null", async () => {
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.landscape).toBe(false)
  })
  test("Reports landscape status as false when viewer is anonymous", () => {
    setViewer({ store, user: genAnon() })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.landscape).toBe(false)
  })
  test("Reports landscape status as false when viewer landscape is false", () => {
    const user = genUser()
    user.landscape = false
    setViewer({ store, user })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.landscape).toBe(false)
  })
  test("Reports landscape status as true when viewer landscape is true", () => {
    const user = genUser()
    user.landscape = true
    setViewer({ store, user })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.landscape).toBe(true)
  })
  test("Returns a guest username when the viewer is a guest.", () => {
    const user = genUser()
    user.guest = true
    user.id = 500
    setViewer({ store, user })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.viewerName).toBe("Guest #500")
  })
  test("Returns a blank username when the viewer is null.", () => {
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.viewerName).toBe("")
  })
  test("Returns a blank username when the viewer is not logged in.", () => {
    setViewer({ store, user: genAnon() })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.viewerName).toBe("")
  })
  test("Identifies the user as a superuser if they are one", async () => {
    setViewer({ store, user: genUser({ is_superuser: true }) })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isSuperuser).toBe(true)
  })
  test("Identifies the user as not a superuser if they are not one", async () => {
    const user = genUser({ is_superuser: false })
    user.is_superuser = false
    setViewer({ store, user })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isSuperuser).toBe(false)
  })
  test("Identifies the user as not a superuser if they are not logged in", async () => {
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isSuperuser).toBe(false)
  })
  test("Identifies the user as a staffer if they are one", async () => {
    setViewer({ store, user: genUser({ is_staff: true }) })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isStaff).toBe(true)
  })
  test("Identifies the user as not a staffer if they are not one", async () => {
    const user = genUser({ is_staff: false })
    user.is_staff = false
    setViewer({ store, user })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isStaff).toBe(false)
  })
  test("Identifies the user as not a staffer if they are not logged in", async () => {
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.isStaff).toBe(false)
  })
  test("Returns a normal username when the viewer is not a guest and is logged in.", () => {
    const user = genUser()
    user.guest = false
    user.username = "TestPerson"
    setViewer({ store, user })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    expect(wrapper.vm.viewerName).toBe("TestPerson")
  })
  test("Prompts for age verification", async () => {
    setViewer({ store, user: genAnon() })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    const vm = wrapper.vm
    expect(store.state.ageAsked).toBe(false)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(0)
    vm.ageCheck({ value: 2 })
    await vm.$nextTick()
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(true)
    expect(store.state.contentRating).toBe(2)
  })
  test("Does not reprompt age verification", async () => {
    setViewer({ store, user: genAnon() })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    const vm = wrapper.vm
    vm.ageCheck({ value: 2 })
    await vm.$nextTick()
    store.commit("setShowAgeVerification", false)
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(2)
    vm.ageCheck({ value: 3 })
    await vm.$nextTick()
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(2)
  })
  test("Forces reprompting", async () => {
    setViewer({ store, user: genAnon() })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    const vm = wrapper.vm
    vm.ageCheck({ value: 2 })
    await nextTick()
    store.commit("setShowAgeVerification", false)
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(2)
    vm.ageCheck({ value: 3, force: true })
    await nextTick()
    expect(store.state.ageAsked).toBe(true)
    expect(store.state.showAgeVerification).toBe(true)
    expect(store.state.contentRating).toBe(3)
  })
  test("Skips if the viewer has set their birthday", async () => {
    setViewer({ store, user: genUser() })
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    const vm = wrapper.vm
    vm.ageCheck({ value: 2 })
    await nextTick()
    expect(store.state.ageAsked).toBe(false)
    expect(store.state.showAgeVerification).toBe(false)
    expect(store.state.contentRating).toBe(0)
  })
  test("Determines the derived rating", async () => {
    wrapper = mount(ViewerComponent, vueSetup({ store }))
    const vm = wrapper.vm
    expect(vm.rawRating).toBe(undefined)
    vm.viewerHandler.user.makeReady(genUser({ rating: Ratings.GENERAL }))
    await vm.$nextTick()
    expect(vm.rawRating).toBe(Ratings.GENERAL)
    vm.viewerHandler.user.updateX({ rating: Ratings.ADULT })
    await vm.$nextTick()
    expect(vm.rawRating).toBe(Ratings.ADULT)
    vm.viewerHandler.user.updateX({ sfw_mode: true })
    await vm.$nextTick()
    expect(vm.rawRating).toBe(Ratings.GENERAL)
  })
})
