import {
  cleanUp,
  mount,
  vueSetup,
  VuetifyWrapped,
} from "@/specs/helpers/index.ts"
import { ArtStore, createStore } from "@/store/index.ts"
import { VueWrapper } from "@vue/test-utils"
import AcCookieConsent from "@/components/AcCookieConsent.vue"
import { deleteCookie, getCookie, setCookie } from "@/lib/lib.ts"
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest"
import { nextTick } from "vue"

const WrappedConsent = VuetifyWrapped(AcCookieConsent)

const clearCookies = () => {
  deleteCookie("cookieOptionsSetV2")
  deleteCookie("firstPartyAnalytics")
  deleteCookie("thirdPartyAnalytics")
}

describe("AcCookieConsent.vue", () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  window._drip = vi.fn()
  window._fb = vi.fn()
  beforeEach(() => {
    store = createStore()
    clearCookies()
  })
  afterEach(() => {
    cleanUp(wrapper)
    clearCookies()
  })
  test("Shows a snackbar when cookie settings are not set.", async () => {
    wrapper = mount(WrappedConsent, vueSetup({ store }))
    expect(wrapper.findComponent(".customize-cookies-button").exists()).toBe(
      true,
    )
  })
  test("Does not show a snackbar when cookie settings are set.", async () => {
    setCookie("cookieOptionsSetV2", "1")
    wrapper = mount(WrappedConsent, vueSetup({ store }))
    expect(wrapper.findComponent(".customize-cookies-button").exists()).toBe(
      false,
    )
  })
  test("Accepts all cookies.", async () => {
    wrapper = mount(WrappedConsent, vueSetup({ store }))
    expect(getCookie("cookieOptionsSetV2")).toBe(null)
    expect(getCookie("firstPartyAnalytics")).toBe(null)
    expect(getCookie("thirdPartyAnalytics")).toBe(null)
    await wrapper.findComponent(".accept-cookies-button").trigger("click")
    await nextTick()
    expect(getCookie("cookieOptionsSetV2")).toBe("1")
    expect(getCookie("firstPartyAnalytics")).toBe("1")
    expect(getCookie("thirdPartyAnalytics")).toBe("1")
  })
  test("Shows a dialog, hiding the snackbar while it is active.", async () => {
    wrapper = mount(WrappedConsent, vueSetup({ store }))
    await nextTick()
    expect(wrapper.findComponent(".dialog-submit").exists()).toBe(false)
    await wrapper.findComponent(".customize-cookies-button").trigger("click")
    await nextTick()
    expect(wrapper.findComponent(".customize-cookies-button").exists()).toBe(
      false,
    )
    expect(wrapper.findComponent(".dialog-submit").exists()).toBe(true)
  })
  test("Enables only essential cookies.", async () => {
    wrapper = mount(WrappedConsent, vueSetup({ store }))
    await nextTick()
    await wrapper.findComponent(".customize-cookies-button").trigger("click")
    await nextTick()
    await wrapper.findComponent(".essential-cookies-button").trigger("click")
    await nextTick()
    expect(wrapper.findComponent(".customize-cookies-button").exists()).toBe(
      false,
    )
    expect(getCookie("cookieOptionsSetV2")).toBe("1")
    expect(getCookie("firstPartyAnalytics")).toBe("0")
    expect(getCookie("thirdPartyAnalytics")).toBe("0")
    expect(store.state.showCookieDialog).toBe(false)
  })
  test("Saves specific cookies.", async () => {
    wrapper = mount(WrappedConsent, vueSetup({ store }))
    await nextTick()
    await wrapper.findComponent(".customize-cookies-button").trigger("click")
    await nextTick()
    await wrapper
      .findComponent(".third-party-analytics")
      .find("input")
      .trigger("click")
    await nextTick()
    await wrapper.findComponent(".dialog-submit").trigger("click")
    expect(wrapper.findComponent(".customize-cookies-button").exists()).toBe(
      false,
    )
    expect(getCookie("cookieOptionsSetV2")).toBe("1")
    expect(getCookie("firstPartyAnalytics")).toBe("1")
    expect(getCookie("thirdPartyAnalytics")).toBe("0")
    expect(store.state.showCookieDialog).toBe(false)
  })
})
