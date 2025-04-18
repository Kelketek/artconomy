import { cleanUp, mount, vueSetup } from "@/specs/helpers/index.ts"
import { ArtStore, createStore } from "@/store/index.ts"
import { VueWrapper } from "@vue/test-utils"
import Payout from "@/components/views/settings/payment/Payout.vue"
import { genUser } from "@/specs/helpers/fixtures.ts"
import { describe, beforeEach, afterEach, test } from "vitest"
import { setViewer } from "@/lib/lib.ts"

let store: ArtStore
let wrapper: VueWrapper<any>

describe("Payout.vue", () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Mounts", async () => {
    setViewer({ store, user: genUser() })
    wrapper = mount(Payout, {
      ...vueSetup({
        store,
        stubs: ["router-link"],
      }),
      props: { username: "Fox" },
    })
  })
})
