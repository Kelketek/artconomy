import {
  cleanUp,
  mockCardMount,
  mount,
  vueSetup,
} from "@/specs/helpers/index.ts"
import { VueWrapper } from "@vue/test-utils"
import AcStripeCharge from "@/components/AcStripeCharge.vue"
import { ArtStore, createStore } from "@/store/index.ts"
import { afterEach, beforeEach, describe, expect, test } from "vitest"

let wrapper: VueWrapper<any>
let store: ArtStore

describe("AcStripeCharge.vue", () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Mounts and preps", async () => {
    wrapper = mount(AcStripeCharge, vueSetup({ store }))
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.card.mount).toBe(mockCardMount)
  })
})
