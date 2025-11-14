import AcCookiedAlert from "@/components/AcCookiedAlert.vue"
import { render, fireEvent, RenderResult } from "@testing-library/vue"
import { beforeEach, afterEach, describe, expect, it } from "vitest"
import { deleteCookie, getCookie } from "@/lib/lib.ts"
import { cleanUp, vueSetup, waitFor } from "@/specs/helpers"

let wrapper: RenderResult

describe("AcCookiedAlert.vue", () => {
  beforeEach(() => {
    deleteCookie("boop")
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it("Displays an alert when there is no cookie.", async () => {
    wrapper = render(AcCookiedAlert, {
      ...vueSetup(),
      slots: { default: "This is test text." },
      props: { cookie: "boop" },
    })
    wrapper.getByText("This is test text.")
    const closeButton = wrapper.getByRole("button")
    await fireEvent.click(closeButton)
    await waitFor(() => expect(wrapper.html()).toEqual(""))
    expect(getCookie("boop")).toBe("read")
  })
  it("Does not display an alert when the time has expired.", () => {
    wrapper = render(AcCookiedAlert, {
      ...vueSetup(),
      slots: { default: "This is test text." },
      props: { cookie: "boop", expires: new Date(2000, 10, 1) },
    })
    expect(() => wrapper.getByText("This is test text.")).throws()
  })
  it("Does not display an alert when the time has not yet arrived.", () => {
    const future = new Date()
    future.setDate(future.getDate() + 5)
    wrapper = render(AcCookiedAlert, {
      ...vueSetup(),
      slots: { default: "This is test text." },
      props: { cookie: "boop", appears: future },
    })
    expect(() => wrapper.getByText("This is test text.")).throws()
  })
  it("Displays an alert when the time has arrived.", () => {
    const past = new Date()
    past.setDate(past.getDate() - 5)
    wrapper = render(AcCookiedAlert, {
      ...vueSetup(),
      slots: { default: "This is test text." },
      props: { cookie: "boop", appears: past },
    })
    wrapper.getByText("This is test text.")
  })
  it("Displays an alert when the time has not expired.", () => {
    const futureDate = new Date()
    futureDate.setDate(futureDate.getDate() + 5)
    wrapper = render(AcCookiedAlert, {
      ...vueSetup(),
      slots: { default: "This is test text." },
      props: { cookie: "boop", expires: futureDate },
    })
    wrapper.getByText("This is test text.")
  })
  it("Displays an alert when the time has arrived and not yet expired.", () => {
    const futureDate = new Date()
    futureDate.setDate(futureDate.getDate() + 5)
    const pastDate = new Date()
    pastDate.setDate(pastDate.getDate() - 5)
    wrapper = render(AcCookiedAlert, {
      ...vueSetup(),
      slots: { default: "This is test text." },
      props: { cookie: "boop", expires: futureDate, appears: pastDate },
    })
    wrapper.getByText("This is test text.")
  })
})
