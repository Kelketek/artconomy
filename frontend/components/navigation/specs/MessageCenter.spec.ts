import { cleanUp, mount, vueSetup, VuetifyWrapped } from "@/specs/helpers"
import { describe, it, beforeEach, afterEach, expect } from "vitest"
import { ArtStore, createStore } from "@/store"
import { setViewer } from "@/lib/lib.ts"
import { genUser } from "@/specs/helpers/fixtures.ts"
import { VueWrapper } from "@vue/test-utils"
import MessageCenter from "@/components/navigation/MessageCenter.vue"

let store: ArtStore
let wrapper: VueWrapper

const WrappedMessageCenter = VuetifyWrapped(MessageCenter)

describe("MessageCenter.vue", () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it("Loads the Sales tab for an artist", async () => {
    const user = genUser()
    setViewer({ store, user: genUser({ artist_mode: true }) })
    wrapper = mount(WrappedMessageCenter, {
      ...vueSetup({ store }),
      props: { username: user.username, modelValue: true },
    })
    const vm = wrapper.findComponent(MessageCenter).vm as any
    expect(vm.section).toEqual(1)
  })
})
