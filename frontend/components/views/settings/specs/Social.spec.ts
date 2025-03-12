import { beforeEach, afterEach, describe, it, expect } from "vitest"
import { render, RenderResult, fireEvent } from "@testing-library/vue"
import Social from "@/components/views/settings/Social.vue"
import {
  cleanUp,
  cloneSetup,
  rs,
  VueMountOptions,
  vueSetup,
  waitFor,
} from "@/specs/helpers"
import { setViewer } from "@/lib/lib.ts"
import { genSocialSettings, genUser } from "@/specs/helpers/fixtures.ts"
import { getList, getSingle } from "@/store/specs/helpers.ts"
import { ArtStore, createStore } from "@/store"
import { SocialLink, SocialSettings } from "@/types/main"
import { nextTick } from "vue"
import mockAxios from "@/specs/helpers/mock-axios.ts"
import { SingleController } from "@/store/singles/controller.ts"
import { ListController } from "@/store/lists/controller.ts"

let options: VueMountOptions
let store: ArtStore
let wrapper: RenderResult

describe("Social.vue", () => {
  let prefs: SocialSettings
  let socialPrefs: SingleController<SocialSettings>
  let socialLinks: ListController<SocialLink>
  beforeEach(() => {
    store = createStore()
    options = vueSetup({ store })
    setViewer({ store, user: genUser({ username: "Fox" }) })
    wrapper = render(Social, {
      ...cloneSetup(options),
      props: { username: "Fox" },
    })
    prefs = genSocialSettings()
    socialPrefs = getSingle<SocialSettings>(
      `Fox__socialPrefs`,
      undefined,
      cloneSetup(options),
    )
    socialLinks = getList<SocialLink>(
      `Fox__socialLinks`,
      undefined,
      cloneSetup(options),
    )
    mockAxios.reset()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it("Updates a social setting.", async () => {
    socialPrefs.makeReady(prefs)
    const promotionField = await waitFor(() =>
      wrapper.getByLabelText("Allow Promotion"),
    )
    expect(promotionField.getAttribute("checked")).toBe(null)
    await fireEvent.click(promotionField)
    await waitFor(() => expect(mockAxios.lastReqGet()).toBeTruthy())
    const req = mockAxios.lastReqGet()
    expect(req.data.allow_promotion).toBeTruthy()
    prefs.allow_promotion = true
    mockAxios.mockResponse(rs(prefs))
    await nextTick()
    expect(promotionField.getAttribute("checked")).toBe("")
  })
  it("Deletes a social link", async () => {
    socialPrefs.makeReady(prefs)
    socialLinks.makeReady([
      {
        id: 50,
        site_name: "Facebook",
        url: "https://facebook.com/boop",
        identifier: "boop",
        comment: "",
      },
    ])
    const deleteButton = await waitFor(() => wrapper.getByLabelText("Delete"))
    await fireEvent.click(deleteButton)
    await waitFor(() => expect(mockAxios.lastReqGet()).toBeTruthy())
    const req = mockAxios.lastReqGet()
    expect(req.method).toBe("delete")
    mockAxios.mockResponse(rs({}))
    await waitFor(() =>
      expect(wrapper.queryAllByLabelText("Delete")).toEqual([]),
    )
  })
  it("Adds a social link", async () => {
    socialPrefs.makeReady(prefs)
    socialLinks.makeReady([])
    const addButton = await waitFor(() => wrapper.getByLabelText("Submit"))
    const input = wrapper.getByLabelText("Profile URL")
    await fireEvent.update(input, "https://facebook.com/boop")
    await fireEvent.click(addButton)
    const req = mockAxios.lastReqGet()
    expect(req.data.url).toBe("https://facebook.com/boop")
    mockAxios.mockResponse(
      rs({
        site_name: "Facebook",
        identifier: "boop",
        id: 5,
        comment: "",
        url: "https://facebook.com/boop",
      }),
    )
    const link = await waitFor(() => wrapper.getByText("boop"))
    expect(link.getAttribute("href")).toBe("https://facebook.com/boop")
  })
})
