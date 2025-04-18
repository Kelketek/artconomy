import AcSettingNav from "@/components/navigation/AcSettingNav.vue"
import { VueWrapper } from "@vue/test-utils"
import { ArtStore, createStore } from "@/store/index.ts"
import { genArtistProfile, genUser } from "@/specs/helpers/fixtures.ts"
import {
  cleanUp,
  createTestRouter,
  mount,
  vueSetup,
} from "@/specs/helpers/index.ts"
import { describe, expect, beforeEach, afterEach, test } from "vitest"
import { Router } from "vue-router"
import { BankStatus } from "@/store/profiles/types/enums.ts"

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe("AcSettingNav.vue", () => {
  beforeEach(() => {
    store = createStore()
    router = createTestRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Shows artist panel when artist mode is on", async () => {
    wrapper = mount(AcSettingNav, {
      ...vueSetup({
        store,
        router,
      }),
      props: { username: "Fox" },
    })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.setX(genUser())
    await wrapper.vm.$nextTick()
    expect(wrapper.find(".artist-panel-link").exists()).toBe(true)
  })
  test("Hides artist panel when artist mode is off", async () => {
    wrapper = mount(AcSettingNav, {
      ...vueSetup({
        store,
        router,
      }),
      props: { username: "Fox" },
    })
    const vm = wrapper.vm as any
    const user = genUser()
    user.artist_mode = false
    vm.subjectHandler.user.setX(user)
    vm.subjectHandler.artistProfile.setX(genArtistProfile())
    await wrapper.vm.$nextTick()
    expect(wrapper.find(".artist-panel-link").exists()).toBe(false)
    expect(wrapper.find(".payout-link").exists()).toBe(false)
  })
  test("Shows payout panel if banking is configured, even if not an artist", async () => {
    wrapper = mount(AcSettingNav, {
      ...vueSetup({
        store,
        router,
      }),
      props: { username: "Fox" },
    })
    const vm = wrapper.vm as any
    const user = genUser()
    user.artist_mode = false
    vm.subjectHandler.user.setX(user)
    const profile = genArtistProfile()
    profile.bank_account_status = BankStatus.IN_SUPPORTED_COUNTRY
    vm.subjectHandler.artistProfile.setX(profile)
    await wrapper.vm.$nextTick()
    expect(wrapper.find(".payout-link").exists()).toBe(true)
  })
})
