import { VueWrapper } from "@vue/test-utils"
import { createVueSocket, socketNameSpace } from "@/plugins/socket.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import WS from "vitest-websocket-mock"
import { genId } from "@/lib/lib.ts"
import { mount, vueSetup } from "@/specs/helpers/index.ts"
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  MockedFunction,
  test,
  vi,
} from "vitest"

let server: WS
let empty: VueWrapper<any>
vi.useRealTimers()

socketNameSpace.socketClass = WebSocket

const initialize = () => {
  server = new WS("ws://test:1234", { jsonProtocol: true })
  const socket = createVueSocket({ endpoint: "ws://test:1234" })
  empty = mount(Empty, vueSetup({ socket }))
}

describe("socket.ts message handlers", () => {
  beforeEach(() => {
    initialize()
  })
  afterEach(() => {
    WS.clean()
  })
  test("Uses a registered handler", async () => {
    const used = vi.fn()
    const used2 = vi.fn()
    const fails = vi.fn()
    const unused = vi.fn()
    const mockError = vi.spyOn(console, "error")
    mockError.mockImplementationOnce(() => undefined)
    fails.mockImplementation(() => {
      throw Error("I broke!")
    })
    empty.vm.$sock.addListener("used", "AppFailed", fails)
    empty.vm.$sock.addListener("used", "Used2", used2)
    empty.vm.$sock.addListener("used", "AppUsed", used)
    empty.vm.$sock.addListener("unused", "AppUnused", unused)
    empty.vm.$sock.open()
    await server.connected
    server.send({ command: "used", payload: { test: "stuff" } })
    expect(unused).not.toHaveBeenCalled()
    expect(used).toHaveBeenCalledWith({ test: "stuff" })
    expect(used2).toHaveBeenCalledWith({ test: "stuff" })
    expect(fails).toHaveBeenCalledWith({ test: "stuff" })
    expect(mockError).toHaveBeenCalledWith(Error("I broke!"))
    server.close()
    await server.closed
  })
  test("Clears handlers", async () => {
    const used = vi.fn()
    const used2 = vi.fn()
    const unused = vi.fn()
    empty.vm.$sock.addListener("used", "Used2", used2)
    empty.vm.$sock.addListener("used", "AppFailed", used)
    empty.vm.$sock.addListener("unused", "AppUnused", unused)
    empty.vm.$sock.removeListener("used", "Used2")
    empty.vm.$sock.removeListener("unused", "AppUnused")
    // Removing a listener that doesn't exist shouldn't break things.
    empty.vm.$sock.removeListener("stuff", "Things")
    empty.vm.$sock.open()
    await server.connected
    server.send({ command: "used", payload: { test: "stuff" } })
    expect(unused).not.toHaveBeenCalled()
    expect(used).toHaveBeenCalledWith({ test: "stuff" })
    expect(used2).not.toHaveBeenCalled()
  })
  test("Skips us if we are excluded", async () => {
    window.windowId = genId()
    const used = vi.fn()
    empty.vm.$sock.addListener("used", "App", used)
    empty.vm.$sock.open()
    await server.connected
    server.send({ command: "used", payload: {}, exclude: [] })
    await empty.vm.$nextTick()
    expect(used).toHaveBeenCalledTimes(1)
    server.send({ command: "used", payload: {} })
    await empty.vm.$nextTick()
    expect(used).toHaveBeenCalledTimes(2)
    server.send({ command: "used", payload: {}, exclude: [window.windowId] })
    await empty.vm.$nextTick()
    expect(used).toHaveBeenCalledTimes(2)
  })
  test("Handles an undefined command", async () => {
    // The command name key is 'name', not 'command'.
    empty.vm.$sock.open()
    await server.connected
    const message = { name: "test", payload: { wat: "do" } }
    expect(() => server.send(message)).toThrow(
      Error(
        `Received undefined command! Message data was: ${JSON.stringify(message)}`,
      ),
    )
  })
  test("Handles a valid command without a listener", async () => {
    // The command name key is 'command', not 'name'.
    empty.vm.$sock.open()
    await server.connected
    server.send({ command: "test", payload: { wat: "do" } })
  })
  test("Sends a message to the server", async () => {
    empty.vm.$sock.open()
    await server.connected
    empty.vm.$sock.send("example", { test: "data" })
    await expect(server).toReceiveMessage({
      command: "example",
      payload: { test: "data" },
    })
  })
})

describe("socket.ts connection handlers", () => {
  let connected: MockedFunction<any>
  let disconnected: MockedFunction<any>
  beforeEach(() => {
    initialize()
    connected = vi.fn()
    disconnected = vi.fn()
    empty.vm.$sock.connectListeners.connected = connected
    empty.vm.$sock.disconnectListeners.disconnected = disconnected
    empty.vm.$sock.open()
  })
  afterEach(() => {
    WS.clean()
  })
  test("Handles a connection", async () => {
    await server.connected
    expect(connected).toHaveBeenCalled()
    expect(disconnected).not.toHaveBeenCalled()
  })
  test("Handles disconnection", async () => {
    await server.connected
    server.close()
    expect(disconnected).toHaveBeenCalled()
  })
  test("Handles forced disconnection", async () => {
    await server.connected
    server.error()
    expect(disconnected).toHaveBeenCalled()
  })
})
