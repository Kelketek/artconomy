import { describe, it, afterEach, beforeEach, expect } from "vitest"
import { ArtStore, createStore } from "@/store"
import {
  cleanUp,
  cloneSetup,
  VueMountOptions,
  vueSetup,
  waitFor,
} from "@/specs/helpers"
import { render, RenderResult } from "@testing-library/vue"
import Promotable from "@/components/views/Promotable.vue"
import { getList } from "@/store/specs/helpers.ts"
import { SocialSettings } from "@/types/main"
import { genSocialSettings, genUser } from "@/specs/helpers/fixtures.ts"
import { User } from "@sentry/vue"

describe("Promotable.spec.ts", () => {
  let store: ArtStore
  let context: VueMountOptions
  let wrapper: RenderResult
  beforeEach(() => {
    store = createStore()
    context = vueSetup({ store })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it("Loads a list of promotable users", async () => {
    wrapper = render(Promotable, cloneSetup(context))
    const promotableUsers = getList<SocialSettings & { user: User }>(
      "promotable_users",
      undefined,
      cloneSetup(context),
    )
    promotableUsers.makeReady([
      {
        ...genSocialSettings({ id: 1 }),
        user: genUser({ username: "Vulpes" }),
      },
      { ...genSocialSettings({ id: 2 }), user: genUser({ username: "Fox" }) },
    ])
    const entries = await waitFor(() => wrapper.getAllByText("Details"))
    expect(entries.length).toBe(2)
  })
})
