import _Vue from 'vue'
import ReconnectingWebSocket, {CloseEvent, Event} from 'reconnecting-websocket'
import {log, neutralize} from '@/lib/lib'

declare interface SocketManager {
  socket?: ReconnectingWebSocket,
  messageListeners: {[key: string]: {[key: string]: Function}},
  connectListeners: {[key: string]: Function},
  disconnectListeners: {[key: string]: Function},
  addListener: (command: string, name: string, func: (any)) => void,
  removeListener: (command: string, name: string) => void,
  endpoint: string,
  send: (command: string, payload: any) => void,
  reset: () => void,
  open: () => void,
}

declare module 'vue/types/vue' {
  // Global properties can be declared
  // on the `VueConstructor` interface
  interface Vue {
    $sock: SocketManager
  }
}

// Super hacky place to put this so it can be mocked out. Side-steps Jest's unbearable module mocker.
export const socketNameSpace: {socketClass: typeof WebSocket|typeof ReconnectingWebSocket} = {
  socketClass: ReconnectingWebSocket,
}

export const VueSocket = {
  install(Vue: typeof _Vue, options: {endpoint: string}): void {
    const $sock: SocketManager = {
      messageListeners: {},
      connectListeners: {},
      disconnectListeners: {},
      endpoint: options.endpoint,
      open() {
        $sock.socket = new ReconnectingWebSocket($sock.endpoint)
        $sock.socket.onopen = (event: Event) => {
          for (const key of Object.keys($sock.connectListeners)) {
            $sock.connectListeners[key](event)
          }
        }
        $sock.socket.onclose = (event: CloseEvent) => {
          for (const key of Object.keys($sock.disconnectListeners)) {
            $sock.disconnectListeners[key](event)
          }
        }
        $sock.socket.onmessage = (event: MessageEvent) => {
          const data = JSON.parse(event.data)
          log.debug('Websocket receive:', data)
          if (!data.command) {
            throw Error(`Received undefined command! Message data was: ${event.data}`)
          }
          if (data.exclude && data.exclude.includes(window.windowId)) {
            // This message is intended to be ignored by the current tab. Useful for when the tab is the one that
            // instigated the command.
            return
          }
          const listeners = Object.values($sock.messageListeners[data.command] || {})
          listeners.push(...(Object.values($sock.messageListeners['*'] || {})))
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
      addListener(command: string, name: string, func: Function) {
        const current = $sock.messageListeners[command] || {}
        current[name] = func
        $sock.messageListeners[command] = current
      },
      removeListener(command: string, name: string) {
        const current = $sock.messageListeners[command] || {}
        delete current[name]
        if (Object.keys(current).length === 0) {
          delete $sock.messageListeners[command]
        }
      },
      send(command: string, payload: any) {
        log.debug('Sending: ', command, payload)
        $sock.socket!.send(JSON.stringify({command, payload}))
      },
      reset() {
        $sock.messageListeners = {}
        $sock.connectListeners = {}
        $sock.disconnectListeners = {}
      },
    }
    neutralize($sock)
    Vue.mixin({
      computed: {
        $sock: () => $sock,
      },
    })
  },
}
