import { Router } from "vue-router"
import {
  cleanUp,
  confirmAction,
  createTestRouter,
  flushPromises,
  mount,
  rs,
  vueSetup,
  waitFor,
} from "@/specs/helpers/index.ts"
import { ArtStore, createStore } from "@/store/index.ts"
import { VueWrapper } from "@vue/test-utils"
import { genUser } from "@/specs/helpers/fixtures.ts"
import ConversationDetail from "@/components/views/ConversationDetail.vue"
import { genConversation } from "@/components/views/specs/fixtures.ts"
import mockAxios from "@/__mocks__/axios.ts"
import { afterEach, beforeEach, describe, expect, test } from "vitest"
import { setViewer } from "@/lib/lib.ts"

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe("ConversationDetail.vue", () => {
  beforeEach(() => {
    store = createStore()
    router = createTestRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Loads a lock toggle for an outside user", async () => {
    const user = genUser()
    user.username = "Dude"
    setViewer({ store, user })
    wrapper = mount(ConversationDetail, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        username: "Fox",
        conversationId: 23,
      },
    })
    const vm = wrapper.vm as any
    vm.conversation.setX(genConversation())
    vm.conversation.fetching = false
    vm.conversation.ready = true
    await vm.$nextTick()
    expect(wrapper.find(".lock-toggle").exists()).toBe(true)
  })
  test("Does not load a lock toggle for an inside user", async () => {
    const user = genUser()
    setViewer({ store, user })
    wrapper = mount(ConversationDetail, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        username: "Fox",
        conversationId: 23,
      },
    })
    const vm = wrapper.vm as any
    vm.conversation.setX(genConversation())
    vm.conversation.fetching = false
    vm.conversation.ready = true
    await vm.$nextTick()
    expect(wrapper.find(".lock-toggle").exists()).toBe(false)
  })
  test("Leaves a conversation", async () => {
    const user = genUser()
    setViewer({ store, user })
    wrapper = mount(ConversationDetail, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        username: "Fox",
        conversationId: 23,
      },
    })
    const vm = wrapper.vm as any
    await router.isReady()
    vm.conversation.setX(genConversation())
    vm.conversation.fetching = false
    vm.conversation.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, [".delete-button"])
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    await vm.$nextTick()
    await waitFor(() =>
      expect(router.currentRoute.value.name).toBe("Conversations"),
    )
  })
})
