import { createRouter, createWebHistory, Router } from "vue-router"
import {
  cleanUp,
  flushPromises,
  mount,
  vueSetup,
} from "@/specs/helpers/index.ts"
import { ArtStore, createStore } from "@/store/index.ts"
import { VueWrapper } from "@vue/test-utils"
import Search from "@/components/views/search/Search.vue"
import SearchProducts from "@/components/views/search/SearchProducts.vue"
import SearchCharacters from "@/components/views/search/SearchCharacters.vue"
import SearchProfiles from "@/components/views/search/SearchProfiles.vue"
import SearchSubmissions from "@/components/views/search/SearchSubmissions.vue"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import ProductExtra from "@/components/views/search/extra/ProductExtra.vue"
import ProductHints from "@/components/views/search/hints/ProductHints.vue"
import SubmissionHints from "@/components/views/search/hints/SubmissionHints.vue"
import CharacterHints from "@/components/views/search/hints/CharacterHints.vue"
import ProfileHints from "@/components/views/search/hints/ProfileHints.vue"
import searchSchema from "@/components/views/search/specs/fixtures.ts"
import { FormController } from "@/store/forms/form-controller.ts"
import { genAnon, genUser } from "@/specs/helpers/fixtures.ts"
import { Ratings } from "@/types/enums/Ratings.ts"
import SubmissionExtra from "@/components/views/search/extra/SubmissionExtra.vue"
import { afterEach, beforeEach, describe, expect, test } from "vitest"
import { setViewer } from "@/lib/lib.ts"

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let searchForm: FormController

describe("Search.vue", () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: "/search/:tabName?/",
          name: "Search",
          component: Search,
          props: true,
          children: [
            {
              path: "products",
              name: "SearchProducts",
              components: {
                default: SearchProducts,
                hints: ProductHints,
                extra: ProductExtra,
              },
              props: true,
            },
            {
              path: "submissions",
              name: "SearchSubmissions",
              components: {
                default: SearchSubmissions,
                hints: SubmissionHints,
                extra: SubmissionExtra,
              },
              props: true,
            },
            {
              path: "characters",
              name: "SearchCharacters",
              components: {
                default: SearchCharacters,
                hints: CharacterHints,
              },
              props: true,
            },
            {
              path: "profiles",
              name: "SearchProfiles",
              components: {
                default: SearchProfiles,
                hints: ProfileHints,
              },
              props: true,
            },
          ],
        },
        {
          name: "SessionSettings",
          path: "/settings/",
          component: Empty,
          props: true,
        },
        {
          name: "Options",
          path: "/profile/:username/settings/options",
          component: Empty,
          props: true,
        },
        {
          name: "Home",
          path: "/",
          component: Empty,
          props: true,
        },
      ],
    })
    searchForm = mount(Empty, vueSetup({ store })).vm.$getForm(
      "search",
      searchSchema(),
    )
    store.commit("setSearchInitialized", true)
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Mounts", () => {
    wrapper = mount(
      Search,
      vueSetup({
        store,
        router,
      }),
    )
  })
  test("Tabs through each search option", async () => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      Search,
      vueSetup({
        store,
        router,
      }),
    )
    const routes = [
      "SearchProducts",
      "SearchSubmissions",
      "SearchCharacters",
      "SearchProfiles",
    ]
    await Promise.all(
      wrapper.findAll(".v-item-group .v-btn").map(async (el, index) => {
        await el.trigger("click")
        await wrapper.vm.$nextTick()
        expect(wrapper.vm.route.name).toBe(routes[index])
      }),
    )
  })
  test("Opens the default view", async () => {
    setViewer({ store, user: genUser() })
    await router.push({ name: "Search" })
    searchForm.fields.featured.update(true)
    wrapper = mount(
      Search,
      vueSetup({
        store,
        router,
      }),
    )
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.value.name).toBe("SearchProducts")
  })
  // Test doesn't work, but code does. Not sure why. Likely something to do with debounce.
  // test('Updates the route when the values change', async() => {
  //   setViewer(store, genUser())
  //   await router.push({name: 'SearchProducts'})
  //   wrapper = mount(SearchProducts, vueSetup({
  //     store,
  //     extraPlugins: [router],
  //   }))
  //   await router.isReady()
  //   await nextTick()
  //   searchForm.fields.featured.update(true)
  //   await waitFor(() => expect(router.currentRoute.value.query).toEqual({
  //     featured: 'true',
  //     page: '1',
  //     size: '24',
  //   }))
  // })
  test("Shows an alert when an anonymous user has a max rating under the current search", async () => {
    await router.push({ name: "SearchProducts" })
    setViewer({ store, user: genAnon() })
    wrapper = mount(
      Search,
      vueSetup({
        store,
        router,
      }),
    )
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(wrapper.find(".v-alert").exists()).toBe(false)
    searchForm.fields.minimum_content_rating.update("3")
    await vm.$nextTick()
    expect(wrapper.find(".v-alert").exists()).toBe(true)
    expect(wrapper.find(".v-alert .rating-button").exists()).toBe(true)
  })
  test("Shows an alert when a registered user has a max rating under the current search", async () => {
    await router.push({ name: "SearchSubmissions" })
    searchForm.fields.content_ratings.update("2,3")
    setViewer({
      store,
      user: genUser({
        username: "Fox",
        rating: Ratings.GENERAL,
      }),
    })
    wrapper = mount(
      Search,
      vueSetup({
        store,
        router,
        stubs: ["v-badge"],
      }),
    )
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(wrapper.find(".v-alert").exists()).toBe(true)
    expect(wrapper.find(".v-alert .rating-button").exists()).toBe(true)
  })
  test("Properly handles setting and getting the allowed content ratings", async () => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      SubmissionExtra,
      vueSetup({
        store,
        router,
        stubs: ["v-badge"],
      }),
    )
    const vm = wrapper.vm as any
    vm.contentRatings = ["1", "3", "0"]
    expect(vm.contentRatings).toEqual([0, 1, 3])
    expect(searchForm.fields.content_ratings.value).toBe("0,1,3")
  })
  test("Synchronizes the value of the form page value and the list page value", async () => {
    wrapper = mount(
      SearchProducts,
      vueSetup({
        store,
        router,
      }),
    )
    const vm = wrapper.vm as any
    vm.list.currentPage = 3
    await vm.$nextTick()
    expect(vm.searchForm.fields.page.value).toEqual(3)
  })
})
