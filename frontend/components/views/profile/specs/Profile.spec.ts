import { VueWrapper } from "@vue/test-utils"
import { ArtStore, createStore } from "@/store/index.ts"
import {
  cleanUp,
  flushPromises,
  mount,
  rq,
  rs,
  vueSetup,
  VuetifyWrapped,
  waitFor,
} from "@/specs/helpers/index.ts"
import { genArtistProfile, genUser } from "@/specs/helpers/fixtures.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import { createRouter, createWebHistory, Router } from "vue-router"
import mockAxios from "@/__mocks__/axios.ts"
import Profile from "@/components/views/profile/Profile.vue"
import { genConversation } from "@/components/views/specs/fixtures.ts"
import { genPricing } from "@/lib/specs/helpers.ts"
import { afterEach, beforeEach, describe, expect, test } from "vitest"
import { setViewer } from "@/lib/lib.ts"
import { User } from "@/store/profiles/types/main"

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let vulpes: User

const WrappedProfile = VuetifyWrapped(Profile)

describe("Profile.vue", () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: "/",
          name: "Home",
          component: Empty,
        },
        {
          path: "/:username/",
          name: "Profile",
          component: Empty,
          children: [
            {
              path: "about",
              component: Empty,
              name: "AboutUser",
            },
            {
              path: "products",
              component: Empty,
              name: "Products",
            },
            {
              path: "characters",
              component: Empty,
              name: "Characters",
            },
            {
              path: "gallery",
              component: Empty,
              name: "Gallery",
            },
            {
              path: "favorite",
              component: Empty,
              name: "Favorites",
            },
            {
              path: "watchlists",
              component: Empty,
              name: "Watchlists",
            },
          ],
        },
        {
          path: "/login/",
          name: "Login",
          component: Empty,
        },
        {
          path: "/:username/settings/",
          name: "Settings",
          component: Empty,
        },
        {
          path: "/:username/messages/:conversationId/",
          name: "Conversation",
          component: Empty,
        },
      ],
    })
    vulpes = genUser()
    vulpes.username = "Vulpes"
    vulpes.is_staff = false
    vulpes.is_superuser = false
    vulpes.id = 2
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Displays a Profile", async () => {
    setViewer({ store, user: vulpes })
    const fox = genUser()
    fox.artist_mode = false
    await router.push({
      name: "Profile",
      params: { username: fox.username },
    })
    wrapper = mount(WrappedProfile, {
      ...vueSetup({
        store,
        router,
      }),
      props: { username: "Fox" },
    })
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/api/profiles/account/Fox/", "get"),
    )
    mockAxios.mockResponse(rs(genPricing()))
    mockAxios.mockResponse(rs(fox))
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/api/profiles/account/Fox/artist-profile/", "get", undefined, {
        params: { view: "true" },
        signal: expect.any(Object),
      }),
    )
    mockAxios.mockResponse(rs(genArtistProfile()))
    // ??? Why ???
    await flushPromises()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await router.isReady()
    await waitFor(() =>
      expect(router.currentRoute.value.name).toBe("AboutUser"),
    )
  })
  test("Displays a default route for an artist", async () => {
    setViewer({ store, user: vulpes })
    const fox = genUser()
    fox.artist_mode = true
    await router.push({
      name: "Profile",
      params: { username: fox.username },
    })
    wrapper = mount(WrappedProfile, {
      ...vueSetup({
        store,
        router,
      }),
      props: { username: "Fox" },
    })
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/api/profiles/account/Fox/", "get"),
    )
    mockAxios.mockResponse(rs(genPricing()))
    mockAxios.mockResponse(rs(fox))
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/api/profiles/account/Fox/artist-profile/", "get", undefined, {
        params: { view: "true" },
        signal: expect.any(Object),
      }),
    )
    mockAxios.mockResponse(rs(genArtistProfile()))
    await flushPromises()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await router.isReady()
    await waitFor(() =>
      expect(router.currentRoute.value.name).toBe("AboutUser"),
    )
  })
  test("Starts a conversation", async () => {
    setViewer({ store, user: vulpes })
    const fox = genUser()
    fox.artist_mode = false
    await router.push({
      name: "Profile",
      params: { username: fox.username },
    })
    wrapper = mount(WrappedProfile, {
      ...vueSetup({
        store,
        router,
      }),
      props: { username: "Fox" },
    })
    mockAxios.mockResponse(rs(genPricing()))
    mockAxios.mockResponse(rs(fox))
    mockAxios.reset()
    await wrapper.vm.$nextTick()
    await wrapper.find(".message-button").trigger("click")
    await wrapper.vm.$nextTick()
    await wrapper.findComponent(".dialog-submit").trigger("click")
    const response = genConversation()
    mockAxios.mockResponse(rs(response))
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.name).toBe("Conversation")
  })
})
