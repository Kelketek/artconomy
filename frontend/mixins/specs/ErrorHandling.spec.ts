import { ArtStore, createStore } from "@/store"
import { VueWrapper } from "@vue/test-utils"
import { afterEach, beforeEach, expect, describe, test } from "vitest"
import { cleanUp, mount, vueSetup } from "@/specs/helpers"
import ErrorComponent from "@/specs/helpers/dummy_components/error.vue"

describe("useErrorHandling", () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Handles a known error status", async () => {
    wrapper = mount(ErrorComponent, vueSetup({ store }))
    const vm = wrapper.vm
    vm.statusOk(403)({ response: { status: 403 } })
  })
  test("Throws on a true error", async () => {
    wrapper = mount(ErrorComponent, vueSetup({ store }))
    const vm = wrapper.vm
    const error = new Error("Beep!")
    expect(() => vm.statusOk(403)(error)).toThrow(error)
  })
})
