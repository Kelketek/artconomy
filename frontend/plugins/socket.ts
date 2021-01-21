import _Vue from 'vue'
import ReconnectingWebSocket from 'reconnecting-websocket'

declare module 'vue/types/vue' {
  // Global properties can be declared
  // on the `VueConstructor` interface
  interface Vue {
    $sock: {
      socket: ReconnectingWebSocket,
      messageListeners: {[key: string]: Function[]},
      connectListeners: Function[],
      disconnectListeners: Function[],
      addListener: (name: string, func: (any)) => void,
      send: (name: string, payload: any) => void,
      reset: () => void,
    },
  }
}

// Super hacky place to put this so it can be mocked out. Side-steps Jest's unbearable module mocker.
export const socketNameSpace = {
  socketClass: ReconnectingWebSocket,
}

export const VueSocket = {
  install(Vue: typeof _Vue, options: {endpoint: string}): void {
    Vue.prototype.$sock = {
      socket: new ReconnectingWebSocket(options.endpoint),
      messageListeners: {},
      connectListeners: [],
      disconnectListeners: [],
      addListener(name: string, func: Function) {
        const current = Vue.prototype.$sock.messageListeners[name] || []
        current.push(func)
        Vue.prototype.$sock.messageListeners[name] = current
      },
      send(name: string, payload: any) {
        Vue.prototype.$sock.socket.send(JSON.stringify({name, payload}))
      },
      reset() {
        Vue.prototype.$sock.messageListeners = {}
        Vue.prototype.$sock.connectListeners = []
        Vue.prototype.$sock.disconnectListeners = []
      },
    }
    Vue.prototype.$sock.socket.onopen = (event: Event) => {
      for (const listener of Vue.prototype.$sock.connectListeners) {
        listener(event)
      }
    }
    Vue.prototype.$sock.socket.onclose = (event: Event) => {
      for (const listener of Vue.prototype.$sock.disconnectListeners) {
        listener(event)
      }
    }
    Vue.prototype.$sock.socket.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data)
      if (!data.name) {
        throw Error(`Received undefined command! Message data was: ${event.data}`)
      }
      const listeners = Vue.prototype.$sock.messageListeners[data.name] || []
      listeners.push(...(Vue.prototype.$sock.messageListeners['*'] || []))
      for (const listener of listeners) {
        try {
          // Reparse each time to assure unique objects.
          listener(JSON.parse(event.data).payload)
        } catch (e) {
          console.error(e)
        }
      }
    }
  },
}
