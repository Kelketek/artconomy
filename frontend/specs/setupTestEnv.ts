// Polyfills the CSS.escape function, needed for dynamic CSS class/identifier creation.
import {clearBody} from '@/specs/helpers'

require('css.escape')
import {expect, vi} from 'vitest'

vi.mock('axios', async (importOriginal) => {
  const realAxios = await importOriginal<typeof import('axios')>()
  const mockAxios = await vi.importActual('vitest-mock-axios')
  return {
    default: mockAxios.default,
    AxiosHeaders: realAxios.AxiosHeaders,
  }
})

export function testName(): string {
  return expect.getState().currentTestName as string
}

export class LocalStorageMock {
    store: {[key: string]: {[key: string]: string}}
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

Object.defineProperty(window, 'localStorage', {value: new LocalStorageMock()})

global.ResizeObserver = require('resize-observer-polyfill')

window.HTMLElement.prototype.scrollIntoView = vi.fn();
window.fbq = vi.fn();

document.hasFocus = () => true
clearBody()
