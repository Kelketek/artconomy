import mockAxios from "./helpers/mock-axios.ts"
import { VueWrapper } from "@vue/test-utils"
import App from "../App.vue"
import { ArtStore, createStore } from "@/store/index.ts"
import flushPromises from "flush-promises"
import { genAnon, genUser } from "./helpers/fixtures.ts"
import { FormController } from "@/store/forms/form-controller.ts"
import {
  cleanUp,
  createTestRouter,
  dialogExpects,
  docTarget,
  mount,
  rq,
  rs,
  vueSetup,
  waitFor,
  waitForSelector,
} from "./helpers/index.ts"
import { WS } from "vitest-websocket-mock"
import { socketNameSpace } from "@/plugins/socket.ts"
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest"
import { nextTick, reactive } from "vue"
import "@/window-type.d.ts"

let wrapper: VueWrapper<typeof App>

socketNameSpace.socketClass = WebSocket

describe("App.vue", () => {
  let store: ArtStore
  const OLD_ENV = process.env
  beforeEach(() => {
    store = createStore()
    process.env = { ...OLD_ENV }
  })
  afterEach(() => {
    cleanUp(wrapper)
    process.env = OLD_ENV
  })
  test("Opens and closes an age verification dialog", async () => {
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: { $route: { fullPath: "/order/", params: {}, query: {} } },
        stubs: ["nav-bar", "router-view", "router-link"],
      }),
    )
    await nextTick()
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    store.commit("setShowAgeVerification", true)
    await nextTick()
    expect(store.state.showAgeVerification).toBe(true)
    expect(vm.viewerHandler.user.x).toBeTruthy()
    await waitForSelector(wrapper, ".dialog-closer")
    await wrapper.findComponent(".dialog-closer").trigger("click")
    await nextTick()
    expect(wrapper.findComponent("dialog-closer").exists()).toBe(false)
  })
  test("Submits the support request form", async () => {
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: { $route: { fullPath: "/", params: {}, query: {} } },
        stubs: ["router-link", "router-view", "nav-bar"],
        attachTo: docTarget(),
      }),
    )
    await nextTick()
    const state = wrapper.vm.store!.state
    expect(state.showSupport).toBe(false)
    const vm = wrapper.vm as any
    expect(vm.showTicketSuccess).toBe(false)
    const supportForm: FormController = (wrapper.vm as any).supportForm
    store.commit("supportDialog", true)
    vm.viewerHandler.user.setX(genUser())
    await nextTick()
    supportForm.fields.body.update("This is a test.")
    await nextTick()
    await waitForSelector(wrapper, "#form-supportRequest")
    const submit = dialogExpects({
      wrapper,
      formName: "supportRequest",
      fields: ["email", "body"],
    })
    submit.trigger("click")
    const response = rq(
      "/api/lib/support/request/",
      "post",
      {
        email: "fox@artconomy.com",
        body: "This is a test.",
        referring_url: "/",
      },
      {},
    )
    expect(mockAxios.request).toHaveBeenCalledWith(response)
    mockAxios.mockResponse(rs(undefined, { status: 204 }))
    await flushPromises()
    expect(state.showSupport).toBe(false)
    expect((wrapper.vm as any).showTicketSuccess).toBe(true)
    const success = wrapper.findComponent("#supportSuccess")
    expect(success.exists()).toBeTruthy()
    await success.find("button").trigger("click")
    expect((wrapper.vm as any).showTicketSuccess).toBe(false)
  })
  test("Updates the email field when the viewer's email is updated.", async () => {
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: {
          $route: { fullPath: "/", params: {}, query: {} },
          $router: { push: vi.fn() },
        },
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    const vm = wrapper.vm as any
    const supportForm = vm.supportForm
    expect(supportForm.fields.email.value).toBe("")
    vm.store.commit("supportDialog", true)
    vm.viewerHandler.user.setX(genUser())
    await nextTick()
    expect(supportForm.fields.email.value).toBe("fox@artconomy.com")
    const editedUser = genUser({ email: "test@example.com" })
    vm.viewerHandler.user.setX(editedUser)
    await nextTick()
    expect(supportForm.fields.email.value).toBe("test@example.com")
    vm.viewerHandler.user.setX(genAnon())
    await nextTick()
    expect(supportForm.fields.email.value).toBe("")
  })
  test("Updates the email field when the viewer's guest email is updated.", async () => {
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: {
          $route: { fullPath: "/", params: {}, query: {} },
          $router: { push: vi.fn() },
        },
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    const vm = wrapper.vm as any
    const supportForm = vm.supportForm
    expect(supportForm.fields.email.value).toBe("")
    vm.viewerHandler.user.setX(genUser())
    await nextTick()
    expect(supportForm.fields.email.value).toBe("fox@artconomy.com")
    const editedUser = genUser({
      email: "test@example.com",
      guest_email: "test2@example.com",
    })
    vm.viewerHandler.user.setX(editedUser)
    await nextTick()
    expect(supportForm.fields.email.value).toBe("test2@example.com")
    vm.viewerHandler.user.setX(genAnon())
    await nextTick()
    expect(supportForm.fields.email.value).toBe("")
  })
  test("Updates the referring_url field when the route has changed.", async () => {
    const router = createTestRouter()
    wrapper = mount(
      App,
      vueSetup({
        store,
        router,
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    const supportForm = (wrapper.vm as any).supportForm
    await router.push("/")
    await nextTick()
    expect(supportForm.fields.referring_url.value).toBe("/")
    await router.push("/faq/about/")
    await waitFor(() =>
      expect(supportForm.fields.referring_url.value).toBe("/faq/about/"),
    )
  })
  test("Shows an alert", async () => {
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: { $route: { fullPath: "/", params: {}, query: {} } },
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    store.commit("pushAlert", { message: "I am an alert!", category: "error" })
    await waitFor(() =>
      expect(wrapper.findComponent(".close-status-alert").exists()).toBe(true),
    )
  })
  test("Removes an alert automatically", async () => {
    // NOTE: This test causes issues with timer cleanup, but there appears to be
    // no solution for this now. The error given by jest about clearing native
    // timers can safely be ignored. The next few tests may also be affected by
    // this issue.
    vi.useFakeTimers()
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: { $route: { fullPath: "/", params: {}, query: {} } },
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    store.commit("pushAlert", { message: "I am an alert!", category: "error" })
    await nextTick()
    vi.runOnlyPendingTimers()
    await nextTick()
    vi.runOnlyPendingTimers()
    await nextTick()
    expect(wrapper.find("#alert-bar").exists()).toBe(false)
    expect((wrapper.vm as any).showAlert).toBe(false)
  })
  test("Resets the alert dismissal value after the alert has cleared.", async () => {
    vi.useFakeTimers()
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: { $route: { fullPath: "/", params: {}, query: {} } },
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    store.commit("pushAlert", { message: "I am an alert!", category: "error" })
    await nextTick()
    vi.runOnlyPendingTimers()
    await nextTick()
    expect((wrapper.vm as any).alertDismissed).toBe(false)
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
  })
  test("Manually resets alert dismissal, if needed", async () => {
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: { $route: { fullPath: "/", params: {}, query: {} } },
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    wrapper.vm.alertDismissed = true
    wrapper.vm.showAlert = true
    expect((wrapper.vm as any).alertDismissed).toBe(false)
  })
  test("Loads up search form data", async () => {
    const router = createTestRouter()
    await router.push("/?q=Stuff")
    wrapper = mount(
      App,
      vueSetup({
        store,
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    const vm = wrapper.vm as any

    await nextTick()
    expect(vm.searchForm.fields.q.value).toBe("Stuff")
  })
  test("Shows the markdown help section", async () => {
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: { $route: { fullPath: "/", params: {}, query: {} } },
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    const vm = wrapper.vm as any
    await nextTick()
    expect(store.state.markdownHelp).toBe(false)
    expect(wrapper.findComponent(".markdown-rendered-help").exists()).toBe(
      false,
    )
    vm.showMarkdownHelp = true
    await nextTick()
    await waitFor(() =>
      expect(wrapper.findComponent(".markdown-rendered-help").exists()).toBe(
        true,
      ),
    )
    expect(store.state.markdownHelp).toBe(true)
    await wrapper.findComponent("#close-markdown-help").trigger("click")
    await nextTick()
    expect(store.state.markdownHelp).toBe(false)
    expect(wrapper.findComponent(".markdown-rendered-help").exists()).toBe(true)
  })
  test("Changes the route key", async () => {
    const router = createTestRouter()
    wrapper = mount(
      App,
      vueSetup({
        store,
        router,
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    const vm = wrapper.vm as any
    await nextTick()
    expect(vm.routeKey).toEqual("")
    await router.push({ name: "Profile", params: { username: "Bob" } })
    await waitFor(() => expect(vm.routeKey).toEqual("username:Bob|"))
    await router.push({
      name: "Character",
      params: { username: "Bob", characterName: "Dude" },
    })
    await waitFor(() =>
      expect(vm.routeKey).toEqual("characterName:Dude|username:Bob|"),
    )
    await router.push({ name: "Submission", params: { submissionId: "555" } })
    await waitFor(() => expect(vm.routeKey).toEqual("submissionId:555|"))
  })
  test("Determines whether or not we are in dev mode", async () => {
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: {
          $route: { fullPath: "/", params: { stuff: "things" }, query: {} },
        },
        stubs: ["router-link", "router-view", "nav-bar"],
      }),
    )
    await nextTick()
    const vm = wrapper.vm as any
    expect(vm.mode()).toBe("test")
    expect(vm.devMode).toBe(false)
    process.env.NODE_ENV = "development"
    vm.recalculate()
    await nextTick()
    await nextTick()
    expect(vm.devMode).toBe(true)
  })
  test("Shows a reconnecting banner if we have lost connection", async () => {
    vi.useRealTimers()
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: {
          $route: { fullPath: "/", params: { stuff: "things" }, query: {} },
        },
        stubs: ["router-link", "router-view", "nav-bar", "ac-cookie-consent"],
      }),
    )
    await nextTick()
    const server = new WS(wrapper.vm.$sock.endpoint)
    await server.connected
    wrapper.vm.socketState.updateX({ serverVersion: "beep" })
    server.close()
    await server.closed
    await nextTick()
    expect(wrapper.findComponent("#reconnection-status-bar").text()).toContain(
      "Reconnecting...",
    )
  })
  test("Resets the connection", async () => {
    vi.useRealTimers()
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: {
          $route: { fullPath: "/", params: { stuff: "things" }, query: {} },
        },
        stubs: ["router-link", "router-view", "nav-bar"],
        attachTo: docTarget(),
      }),
    )
    await nextTick()
    const vm = wrapper.vm
    const server = new WS(wrapper.vm.$sock.endpoint, { jsonProtocol: true })
    // Need to make sure the cookie for the socket key is set, which can happen on next tick.
    await nextTick()
    const mockClose = vi.spyOn(vm.$sock.socket!, "close")
    const mockReconnect = vi.spyOn(vm.$sock.socket!, "reconnect")
    await server.connected
    expect(mockClose).not.toHaveBeenCalled()
    expect(mockReconnect).not.toHaveBeenCalled()
    server.send({ command: "reset", payload: {} })
    await nextTick()
    expect(mockClose).toHaveBeenCalledTimes(1)
    await new Promise((resolve) => setTimeout(resolve, 3000))
    expect(mockReconnect).toHaveBeenCalledTimes(1)
  })
  test("Sets the viewer", async () => {
    vi.useRealTimers()
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: {
          $route: { fullPath: "/", params: { stuff: "things" }, query: {} },
        },
        stubs: ["router-link", "router-view", "nav-bar"],
        attachTo: docTarget(),
      }),
    )
    await nextTick()
    const server = new WS(wrapper.vm.$sock.endpoint, { jsonProtocol: true })
    await server.connected
    const person = genUser({ username: "Person" })
    server.send({ command: "viewer", payload: person })
    const vm = wrapper.vm as any
    await nextTick()
    expect(vm.viewer.username).toBe("Person")
  })
  test("Gets the current version", async () => {
    vi.useRealTimers()
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: {
          $route: { fullPath: "/", params: { stuff: "things" }, query: {} },
        },
        stubs: ["router-link", "router-view", "nav-bar"],
        attachTo: docTarget(),
      }),
    )
    await nextTick()
    const server = new WS(wrapper.vm.$sock.endpoint, { jsonProtocol: true })
    await server.connected
    await expect(server).toReceiveMessage({ command: "version", payload: {} })
    server.send({ command: "version", payload: { version: "beep" } })
    await nextTick()
    const vm = wrapper.vm as any
    expect(vm.socketState.x.serverVersion).toEqual("beep")
  })
  test("Emits a tracking event", async () => {
    vi.useRealTimers()
    const router = createTestRouter()
    wrapper = mount(
      App,
      vueSetup({
        store,
        router,
        mocks: reactive({
          $route: {
            fullPath: "/",
            params: { stuff: "things" },
            name: "Home",
            query: {},
          },
        }),
        stubs: ["router-link", "router-view", "nav-bar"],
        attachTo: docTarget(),
      }),
    )
    await nextTick()
    await nextTick()
    window._paq = []
    await router.push("/submissions/35")
    await nextTick()
    await nextTick()
    expect(window._paq).toEqual([
      ["setCustomUrl", "http://localhost:3000/submissions/35"],
      ["setDocumentTitle", ""],
      ["setReferrerUrl", "http://localhost:3000/"],
      ["trackPageView"],
    ])
    await router.push({ name: "FAQ" })
    window._paq = []
    // Should not send a tracking event, but others should be tracked.
    await nextTick()
    await nextTick()
    expect(window._paq).toEqual([
      ["setCustomUrl", "http://localhost:3000/faq/"],
      ["setDocumentTitle", ""],
      ["setReferrerUrl", "http://localhost:3000/submissions/35"],
    ])
  })
})
