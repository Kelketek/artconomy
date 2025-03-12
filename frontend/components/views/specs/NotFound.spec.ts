import { shallowMount, VueWrapper } from "@vue/test-utils"
import NotFound from "../NotFound.vue"
import { ArtStore, createStore } from "@/store/index.ts"
import { cleanUp, vueSetup } from "@/specs/helpers/index.ts"
import { afterEach, beforeEach, describe, expect, test } from "vitest"

let wrapper: VueWrapper<any>

describe("NotFound.vue", () => {
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Sets the error code upon creation", async () => {
    wrapper = shallowMount(NotFound, vueSetup({ store }))
    expect((store.state as any).errors.code).toBe(404)
  })
})
