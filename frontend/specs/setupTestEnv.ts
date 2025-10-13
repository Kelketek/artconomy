// Polyfills the CSS.escape function, needed for dynamic CSS class/identifier creation.
import { clearBody } from "@/specs/helpers"

import "css.escape"
import { expect, vi } from "vitest"
import ResizeObserver from "resize-observer-polyfill"
import "@/window-type.d.ts"

vi.mock("axios", async (importOriginal) => {
  const realAxios = await importOriginal<typeof import("axios")>()
  const mockAxios = await vi.importActual("@artconomy/vitest-mock-axios")
  return {
    default: mockAxios.default,
    AxiosHeaders: realAxios.AxiosHeaders,
  }
})

export function testName(): string {
  return expect.getState().currentTestName as string
}

export class LocalStorageMock {
  store: { [key: string]: { [key: string]: string } }
  constructor() {
    this.store = {}
  }

  clear() {
    delete this.store[testName()]
  }

  getItem(key: string) {
    const specStore = this.store[testName()] || {}
    return specStore[key] || null
  }

  setItem(key: string, value: any) {
    const name = testName()
    if (!this.store[name]) {
      this.store[name] = {}
    }
    this.store[name][key] = value.toString()
  }

  removeItem(key: string) {
    delete this.store[testName()][key]
  }
}

Object.defineProperty(window, "localStorage", {
  value: new LocalStorageMock(),
})

global.ResizeObserver = ResizeObserver

window.HTMLElement.prototype.scrollIntoView = vi.fn()
window.scrollTo = vi.fn()
window.fbq = vi.fn()

document.hasFocus = () => true
clearBody()

const IntersectionObserverMock = vi.fn(() => ({
  disconnect: vi.fn(),
  observe: vi.fn(),
  takeRecords: vi.fn(),
  unobserve: vi.fn(),
}))

vi.stubGlobal("IntersectionObserver", IntersectionObserverMock)

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

vi.stubGlobal("visualViewport", new EventTarget())
