import { VueWrapper } from "@vue/test-utils"
import AcConfirmation from "../AcConfirmation.vue"
import {
  mount,
  vueSetup,
  confirmAction,
  waitFor,
} from "@/specs/helpers/index.ts"
import { describe, expect, test, vi } from "vitest"
import { VCard } from "vuetify/components"

let wrapper: VueWrapper<any>

describe("AcConfirmation.vue", () => {
  test("Calls the action when sending", async () => {
    const action = vi.fn()
    action.mockImplementation(
      () =>
        new Promise<void>((resolve) => {
          resolve()
        }),
    )
    wrapper = mount(AcConfirmation, {
      ...vueSetup(),
      props: { action },
    })
    const dialog = wrapper.findComponent(VCard)
    expect(dialog.exists()).toBe(false)
    await confirmAction(wrapper, [".confirm-launch"])
    expect(action).toHaveBeenCalled()
    await waitFor(() =>
      expect(wrapper.findComponent(".confirmation-modal-active").exists()).toBe(
        false,
      ),
    )
  })
})
