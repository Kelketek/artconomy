import { createRouter, Router } from "vue-router"
import { faqRoutes } from "./helpers.ts"
import { VueWrapper } from "@vue/test-utils"
import { ArtStore, createStore } from "@/store/index.ts"
import About from "@/components/views/faq/About.vue"
import {
  cleanUp,
  flushPromises,
  mount,
  vueSetup,
} from "@/specs/helpers/index.ts"
import { afterEach, beforeEach, describe, expect, test } from "vitest"

describe("About.vue", () => {
  let router: Router
  let wrapper: VueWrapper<any>
  let store: ArtStore
  beforeEach(() => {
    router = createRouter(faqRoutes())
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("mounts", async () => {
    await router.push("/faq/about/")
    wrapper = mount(
      About,
      vueSetup({
        store,
        router,
      }),
    )
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.params).toEqual({
      question: "what-is-artconomy",
    })
  })
  test("sets a question", async () => {
    await router.push("/faq/about/what-is-artconomy/")
    wrapper = mount(
      About,
      vueSetup({
        store,
        router,
      }),
    )
    await wrapper.vm.$nextTick()
    const header = wrapper.findAll(".v-expansion-panel-title").at(1)!
    await header.trigger("click")
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.params).toEqual({ question: "cost" })
  })
})
