import { VueWrapper } from "@vue/test-utils"
import AcTgDevice from "../AcTgDevice.vue"
import { ArtStore, createStore } from "@/store/index.ts"
import {
  cleanUp,
  flushPromises,
  mount,
  rq,
  vueSetup,
  waitFor,
} from "@/specs/helpers/index.ts"
import { genUser } from "@/specs/helpers/fixtures.ts"
import { ListController } from "@/store/lists/controller.ts"
import mockAxios from "@/specs/helpers/mock-axios.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import { describe, expect, beforeEach, afterEach, test, vi } from "vitest"
import { setViewer } from "@/lib/lib.ts"
import { nextTick } from "vue"
import { TOTPDevice } from "@/types/main"

const qrImageUrl =
  "otpauth://totp/Artconomy%20Dev%3Afox%40vulpinity.com?secret=KJZWLZLDMVY3XJAX72V4WAXDKKZZDA76" +
  "&algorithm=SHA1&digits=6&period=30&issuer=Artconomy+Dev"

describe("AcTgDevice.vue", () => {
  const mockError = vi.spyOn(console, "error")
  let store: ArtStore
  let wrapper: VueWrapper<any>
  let controller: ListController<TOTPDevice>
  beforeEach(() => {
    store = createStore()
    controller = mount(Empty, vueSetup({ store })).vm.$getList("totpDevices", {
      endpoint: "/test/",
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Shows a set of steps", async () => {
    setViewer({ store, user: genUser() })
    controller.setList([
      {
        id: 1,
        confirmed: false,
        config_url: qrImageUrl,
        name: "Phone",
      },
    ])
    wrapper = mount(AcTgDevice, {
      ...vueSetup({ store }),
      props: {
        username: "Fox",
        device: controller.list[0],
      },
    })
    expect(wrapper.findAll(".v-stepper-window-item").length).toBe(3)
  })
  test("Shows no steps if the device is confirmed", async () => {
    setViewer({ store, user: genUser() })
    controller.setList([
      {
        id: 1,
        confirmed: true,
        config_url: qrImageUrl,
        name: "Phone",
      },
    ])
    wrapper = mount(AcTgDevice, {
      ...vueSetup({ store }),
      props: {
        username: "Fox",
        device: controller.list[0],
      },
    })
    expect(wrapper.findAll(".v-stepper__step").length).toBe(0)
  })
  test("Deletes a device", async () => {
    setViewer({ store, user: genUser() })
    controller.setList([
      {
        id: 1,
        confirmed: true,
        config_url: qrImageUrl,
        name: "Phone",
      },
    ])
    wrapper = mount(AcTgDevice, {
      ...vueSetup({ store }),
      props: {
        username: "Fox",
        device: controller.list[0],
      },
    })
    mockAxios.reset()
    await wrapper.findComponent(".delete-phone-2fa").trigger("click")
    await nextTick()
    await wrapper.findComponent(".confirmation-button").trigger("click")
    expect(mockAxios.request).toHaveBeenCalledWith(rq("/test/1/", "delete"))
    mockAxios.mockResponse({
      status: 204,
      data: {},
    })
    await flushPromises()
    expect(controller.list).toEqual([])
  })
  test("Sends a telegram code", async () => {
    setViewer({ store, user: genUser() })
    mockError.mockImplementationOnce(() => undefined)
    controller.setList([
      {
        id: 1,
        confirmed: false,
        config_url: qrImageUrl,
        name: "Phone",
      },
    ])
    wrapper = mount(AcTgDevice, {
      ...vueSetup({ store }),
      props: {
        username: "Fox",
        device: controller.list[0],
      },
    })
    wrapper.vm.step = 2
    await nextTick()
    await wrapper.find(".send-tg-code").trigger("click")
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq(
        "/api/profiles/account/Fox/auth/two-factor/tg/",
        "post",
        undefined,
        {},
      ),
    )
  })
  // This test appears to have some unknown isolation issue. It works when meaninglessly modified so that a test rerun
  // is triggered.
  test("Sends a verification code", async () => {
    setViewer({ store, user: genUser() })
    mockError.mockImplementationOnce(() => undefined)
    controller.setList([
      {
        id: 1,
        confirmed: false,
        config_url: qrImageUrl,
        name: "Phone",
      },
    ])
    wrapper = mount(AcTgDevice, {
      ...vueSetup({ store }),
      props: {
        username: "Fox",
        device: controller.list[0],
      },
    })
    const empty = mount(Empty, vueSetup({ store })).vm
    const form = empty.$getForm("telegramOTP")
    form.fields.code.update("123456")
    wrapper.vm.step = 3
    await waitFor(() => wrapper.find(".submit-button").trigger("click"))
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq(
        "/api/profiles/account/Fox/auth/two-factor/tg/",
        "patch",
        { code: "123 456" },
        {},
      ),
    )
  })
  test("Updates the form URL if the username changes", async () => {
    const user = genUser()
    user.username = "Vulpes"
    setViewer({ store, user: genUser() })
    await store.dispatch("profiles/saveUser", user)
    controller.setList([
      {
        id: 1,
        confirmed: true,
        config_url: qrImageUrl,
        name: "Phone",
      },
    ])
    wrapper = mount(AcTgDevice, {
      ...vueSetup({ store }),
      props: {
        username: "Fox",
        device: controller.list[0],
      },
    })
    expect(wrapper.vm.url).toBe("/api/profiles/account/Fox/auth/two-factor/tg/")
    await wrapper.setProps({
      username: "Vulpes",
      device: { ...controller.list[0] },
    })
    await nextTick()
    expect(wrapper.vm.url).toBe(
      "/api/profiles/account/Vulpes/auth/two-factor/tg/",
    )
    expect(wrapper.vm.form.endpoint).toBe(
      "/api/profiles/account/Vulpes/auth/two-factor/tg/",
    )
  })
})
