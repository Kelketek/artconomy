import { createRouter, createWebHistory, Router } from "vue-router"
import { cleanUp, mount, vueSetup } from "@/specs/helpers/index.ts"
import { ArtStore, createStore } from "@/store/index.ts"
import { VueWrapper } from "@vue/test-utils"
import AcTab from "@/components/AcTab.vue"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import { afterEach, beforeEach, describe, expect, test } from "vitest"

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe("AcTab.vue", () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          name: "Place",
          component: Empty,
          path: "/place/",
        },
        {
          name: "Home",
          component: Empty,
          path: "/",
        },
      ],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Renders list tab information", async () => {
    const list = mount(Empty, vueSetup({ store })).vm.$getList("stuff", {
      endpoint: "/",
    })
    list.fetching = false
    list.ready = true
    wrapper = mount(AcTab, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        trackPages: true,
        to: { name: "Place" },
        list,
      },
    })
    const vm = wrapper.vm as any
    expect(vm.destination).toEqual({ name: "Place" })
    list.currentPage = 3
    list.response = {
      count: 24,
      size: 5,
    }
    list.fetching = true
    list.ready = true
    await wrapper.vm.$nextTick()
    expect(vm.destination).toEqual({
      name: "Place",
      query: { page: "3" },
    })
  })
  test("Links to a destination", async () => {
    wrapper = mount(AcTab, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        trackPages: false,
        to: { name: "Place" },
      },
    })
    const vm = wrapper.vm as any
    expect(vm.destination).toEqual({ name: "Place" })
  })
  test("Links to nowhere", async () => {
    wrapper = mount(AcTab, {
      ...vueSetup({
        store,
        router,
      }),
      props: {},
    })
    const vm = wrapper.vm as any
    expect(vm.destination).toBe(undefined)
  })
})
