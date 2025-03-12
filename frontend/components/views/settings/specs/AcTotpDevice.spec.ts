import { VueWrapper } from "@vue/test-utils"
import AcTotpDevice from "../AcTotpDevice.vue"
import { ArtStore, createStore } from "@/store/index.ts"
import {
  cleanUp,
  flushPromises,
  mount,
  rq,
  vueSetup,
  VuetifyWrapped,
  waitForSelector,
} from "@/specs/helpers/index.ts"
import { genUser } from "@/specs/helpers/fixtures.ts"
import { ListController } from "@/store/lists/controller.ts"
import mockAxios from "@/specs/helpers/mock-axios.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import { describe, expect, beforeEach, afterEach, test } from "vitest"
import { setViewer } from "@/lib/lib.ts"
import { nextTick } from "vue"
import { TOTPDevice } from "@/types/main"

const qrImageUrl =
  "otpauth://totp/Artconomy%20Dev%3Afox%40vulpinity.com?secret=KJZWLZLDMVY3XJAX72V4WAXDKKZZDA76" +
  "&algorithm=SHA1&digits=6&period=30&issuer=Artconomy+Dev"

const WrappedDevice = VuetifyWrapped(AcTotpDevice)

describe("AcTotpDevice.vue", () => {
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
    wrapper = mount(WrappedDevice, {
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
    wrapper = mount(WrappedDevice, {
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
    wrapper = mount(WrappedDevice, {
      ...vueSetup({ store }),
      props: {
        username: "Fox",
        device: controller.list[0],
      },
    })
    mockAxios.reset()
    await wrapper.find(".delete-phone-2fa").trigger("click")
    await wrapper.vm.$nextTick()
    await wrapper.findComponent(".confirmation-button").trigger("click")
    expect(mockAxios.request).toHaveBeenCalledWith(rq("/test/1/", "delete"))
    mockAxios.mockResponse({
      status: 204,
      data: null,
    })
    await flushPromises()
    expect(controller.list).toEqual([])
  })
  test("Sends a verification code", async () => {
    setViewer({ store, user: genUser() })
    controller.setList([
      {
        id: 1,
        confirmed: false,
        config_url: qrImageUrl,
        name: "Phone",
      },
    ])
    wrapper = mount(AcTotpDevice, {
      ...vueSetup({ store }),
      props: {
        username: "Fox",
        device: controller.list[0],
      },
    })
    const form = wrapper.vm.$getForm("1_totpForm")
    form.fields.code.update("123456")
    wrapper.vm.step = 3
    await nextTick()
    mockAxios.reset()
    await waitForSelector(wrapper, ".submit-button")
    await wrapper.find(".submit-button").trigger("click")
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/test/1/", "patch", { code: "123 456" }, {}),
    )
  })
})
