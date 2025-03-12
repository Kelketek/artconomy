import { VueWrapper } from "@vue/test-utils"
import AcCard from "@/components/views/settings/payment/AcCard.vue"
import { ArtStore, createStore } from "@/store/index.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import {
  cleanUp,
  flushPromises,
  mount,
  rq,
  rs,
  vueSetup,
  waitFor,
} from "@/specs/helpers/index.ts"
import { ListController } from "@/store/lists/controller.ts"
import mockAxios from "@/__mocks__/axios.ts"
import { describe, expect, beforeEach, afterEach, test, vi } from "vitest"
import { VCard } from "vuetify/components"
import AcConfirmation from "@/components/wrappers/AcConfirmation.vue"
import { nextTick } from "vue"
import type { CreditCardToken } from "@/types/main"

let store: ArtStore
let wrapper: VueWrapper<any>
let generator: VueWrapper<any>
let cardList: ListController<CreditCardToken>

describe("AcCard.vue", () => {
  beforeEach(() => {
    store = createStore()
    generator = mount(Empty, vueSetup({ store }))
    cardList = generator.vm.$getList("creditCards", { endpoint: "/cards/" })
    cardList.setList([
      {
        id: 1,
        last_four: "1234",
        primary: true,
        type: 1,
        cvv_verified: true,
      },
    ])
    wrapper = mount(AcCard, {
      ...vueSetup({ store }),
      props: {
        cardList,
        card: cardList.list[0],
      },
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Mounts and displays a card", async () => {
    await waitFor(() => expect(wrapper.find(".ac-Visa").exists()).toBe(true))
    expect(wrapper.find(".default-indicator").exists()).toBe(true)
  })
  test("Deletes a card", async () => {
    const mockGet = vi.spyOn(cardList, "get")
    const confirm = await waitFor(() => wrapper.getComponent(AcConfirmation))
    await wrapper.find(".delete-card").trigger("click")
    // Confirmation.
    await nextTick()
    const dialog = confirm.findComponent(VCard)
    await dialog.find(".delete-confirm .confirmation-button").trigger("click")
    expect(mockAxios.request).toHaveBeenCalledWith(rq("/cards/1/", "delete"))
    mockAxios.mockResponse({
      status: 204,
      data: {},
    })
    await flushPromises()
    await nextTick()
    expect(mockGet).toHaveBeenCalled()
  })
  test("Marks a card as primary", async () => {
    cardList.list[0].updateX({ primary: false })
    cardList.push({
      id: 2,
      cvv_verified: true,
      last_four: "5432",
      primary: true,
      type: 2,
    })
    cardList.push({
      id: 3,
      cvv_verified: true,
      last_four: "4563",
      primary: false,
      type: 3,
    })
    cardList.list[2].setX(null)
    await nextTick()
    await wrapper.find(".make-default").trigger("click")
    // Confirmation.
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/cards/1/primary/", "post", undefined, {}),
    )
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    expect((cardList.list[0].x as CreditCardToken).primary).toBe(true)
    expect((cardList.list[1].x as CreditCardToken).primary).toBe(false)
  })
  test("Shows the correct icon for a card", async () => {
    const vm = wrapper.vm
    vm.card.updateX({ type: 1 })
    await nextTick()
    await waitFor(() => expect(wrapper.find(".ac-Visa").exists()).toBe(true))
    vm.card.updateX({ type: 2 })
    await flushPromises()
    await nextTick()
    expect(wrapper.find(".ac-MasterCard").exists()).toBe(true)
    vm.card.updateX({ type: 80 })
    await nextTick()
    // This will never actually be displayed, because a non-existent card shouldn't be rendered.
    expect(wrapper.find(".ac-unknown-card").exists()).toBe(true)
  })
})
