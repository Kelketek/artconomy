
export function testName() {
    return expect.getState().currentTestName
}

class LocalStorageMock {
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
