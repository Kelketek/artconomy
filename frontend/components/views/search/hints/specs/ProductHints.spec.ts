import { cleanUp, mount, vueSetup } from "@/specs/helpers/index.ts"
import { VueWrapper } from "@vue/test-utils"
import ProductHints from "@/components/views/search/hints/ProductHints.vue"
import searchSchema from "@/components/views/search/specs/fixtures.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import { ArtStore, createStore } from "@/store/index.ts"
import { genUser } from "@/specs/helpers/fixtures.ts"
import { afterEach, beforeEach, describe, expect, test } from "vitest"
import { setViewer } from "@/lib/lib.ts"

let wrapper: VueWrapper<any>
let store: ArtStore

describe("ProductHints.vue", () => {
  beforeEach(() => {
    store = createStore()
    setViewer({ store, user: genUser() })
    mount(Empty, vueSetup({ store })).vm.$getForm("search", searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Performs a search", async () => {
    wrapper = mount(ProductHints, vueSetup({ store }))
    await wrapper.find(".v-chip__content").trigger("click")
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.searchForm.fields.q.value).toBe("refsheet")
  })
})
