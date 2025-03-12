import { describe, it, expect, afterEach } from "vitest"
import { cleanUp, mount, vueSetup } from "@/specs/helpers"
import AcStatsBar from "@/components/navigation/AcStatsBar.vue"
import flushPromises from "flush-promises"
import { VueWrapper } from "@vue/test-utils"
import { nextTick } from "vue"

let wrapper: VueWrapper<typeof AcStatsBar>

describe("AcStatsBar.vue", () => {
  afterEach(() => {
    cleanUp(wrapper)
  })
  it("Shows stats", async () => {
    wrapper = mount(AcStatsBar, { ...vueSetup(), props: { username: "Fox" } })
    await flushPromises()
    expect(wrapper.vm.stats.fetching).toBeTruthy()
    wrapper.vm.stats.setX({
      new_orders: 3,
      active_orders: 5,
    })
    await nextTick()
    expect(wrapper.find(".active-order-count").text()).toEqual("5")
    expect(wrapper.find('[role="status"]').text()).toEqual("3")
  })
  it("Does not show a badge when there are no new orders", async () => {
    wrapper = mount(AcStatsBar, { ...vueSetup(), props: { username: "Fox" } })
    await flushPromises()
    expect(wrapper.vm.stats.fetching).toBeTruthy()
    wrapper.vm.stats.setX({
      new_orders: 0,
      active_orders: 5,
    })
    await nextTick()
    expect(wrapper.find(".active-order-count").text()).toEqual("5")
    expect(wrapper.find('[role="status"]').isVisible()).toBe(false)
  })
})
