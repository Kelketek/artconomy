import { VueWrapper } from "@vue/test-utils"
import Editable from "@/specs/helpers/dummy_components/editable.vue"
import {
  cleanUp,
  createTestRouter,
  mount,
  vueSetup,
  waitFor,
} from "@/specs/helpers/index.ts"
import { afterEach, beforeEach, describe, expect, test } from "vitest"
import { Router } from "vue-router"

let router: Router

describe("Editable.ts", () => {
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    router = createTestRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Reports when editing", async () => {
    await router.push("/?editing=true")
    wrapper = mount(Editable, {
      props: { controls: true },
      ...vueSetup({ router }),
    })
    expect(wrapper.vm.editing).toBe(true)
  })
  test("Reports when not editing", async () => {
    await router.push("/")
    wrapper = mount(Editable, {
      props: { controls: true },
      ...vueSetup({ router }),
    })
    expect(wrapper.vm.editing).toBe(false)
  })
  test("Reports not editing if controls is false", async () => {
    await router.push("/?editing=true")
    wrapper = mount(Editable, {
      props: { controls: false },
      ...vueSetup({ router }),
    })
    expect(wrapper.vm.editing).toBe(false)
  })
  test("Locks the view", async () => {
    await router.push("/?editing=true&what=things")
    wrapper = mount(Editable, {
      props: { controls: true },
      ...vueSetup({ router }),
    })
    wrapper.vm.editing = false
    await waitFor(() =>
      expect(router.currentRoute.value.query).toEqual({ what: "things" }),
    )
  })
  test("Unlocks the view", async () => {
    await router.push("/?what=things")
    wrapper = mount(Editable, {
      props: { controls: true },
      ...vueSetup({ router }),
    })
    wrapper.vm.editing = true
    await waitFor(() =>
      expect(router.currentRoute.value.query).toEqual({
        what: "things",
        editing: "true",
      }),
    )
  })
})
