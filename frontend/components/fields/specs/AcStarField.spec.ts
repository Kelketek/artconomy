import { mount, vueSetup } from "@/specs/helpers/index.ts"
import { ArtStore, createStore } from "@/store/index.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import AcStarField from "@/components/fields/AcStarField.vue"
import { describe, expect, beforeEach, test } from "vitest"

let store: ArtStore

describe("AcSavedCardField.vue", () => {
  beforeEach(() => {
    store = createStore()
  })
  test("Sends the right information", async () => {
    mount(Empty, vueSetup({ store }))
    const wrapper = mount(AcStarField, {
      ...vueSetup({ store }),
      props: {
        modelValue: null,
      },
    })
    await wrapper.findAll(".v-icon").at(2)!.trigger("click")
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted("update:modelValue")![0]).toEqual([3])
  })
})
