/* This is run after initial Jest environment setup. It has access to the Jest globals, so we can access expect here. */

// Polyfills the CSS.escape function, needed for dynamic CSS class/identifier creation.
require('css.escape')

export function testName() {
  return expect.getState().currentTestName
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

// @ts-ignore
window.ResizeObserver = window.ResizeObserver || jest.fn().mockImplementation(() => ({
  disconnect: jest.fn(),
  observe: jest.fn(),
  unobserve: jest.fn(),
}))
