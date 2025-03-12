import "vite/modulepreload-polyfill"
import { init, browserTracingIntegration, replayIntegration } from "@sentry/vue"
import { createApp, h } from "vue"
import { createStore } from "@/store/index.ts"
import App from "./App.vue"
import { configureHooks, router } from "@/router/index.ts"
import { createForms } from "@/store/forms/registry.ts"
import { Shortcuts } from "./plugins/shortcuts.ts"
import supportedBrowsers from "./supportedBrowsers.ts"
import { genId, loadErrorHandler, setViewer } from "./lib/lib.ts"
import { createLists } from "@/store/lists/registry.ts"
import { createSingles } from "@/store/singles/registry.ts"
import { createProfiles } from "@/store/profiles/registry.ts"
import { createCharacters } from "@/store/characters/registry.ts"
import { createVueSocket } from "@/plugins/socket.ts"
import { createVuetify } from "@/plugins/vuetify.ts"
import "@stripe/stripe-js"
import { VCol, VRow } from "vuetify/lib/components/VGrid/index.mjs"
import { createTargetsPlugin } from "@/plugins/targets.ts"
import { createRegistries } from "@/plugins/createRegistries.ts"
import "@/window-type.d.ts"

// Uncomment to enable debug logger.
// window.__LOG_LEVEL__ = 0

const productionMode = process.env.NODE_ENV === "production"
if (!productionMode) {
  // @ts-expect-error Style must be dependently imported.
  import("vuetify/styles")
}

const app = createApp({
  components: { App, VCol, VRow },
  render: () => h(App),
})
const store = createStore()
const loadHandler = loadErrorHandler(store)
router.onError(loadHandler)
addEventListener("unhandledrejection", loadHandler)

app.use(router)
app.use(store)
app.use(
  createVueSocket({ endpoint: `wss://${window.location.host}/ws/events/` }),
)
app.use(Shortcuts)
app.use(createVuetify())
app.use(createLists(store))
app.use(createForms(store))
app.use(createSingles(store))
app.use(createCharacters(store))
app.use(createProfiles(store))
app.use(createRegistries())
app.use(createTargetsPlugin(false))

setViewer({ store, user: window.USER_PRELOAD })

window.artconomy = app

// The 'window ID' is used to distinguish one tab from another when making requests to the server. This is useful for
// some websocket activities where one tab is the originator of a change and others need to pick it up.
window.windowId = genId()

if (productionMode) {
  const splash = `
!!!WARNING!!! This is for advanced users. DO NOT paste anything you don't understand into this console. If you do,
your account security could be at risk!

If you DO know how to use this console, please geek out with us in the #tech-nerd-zone channel on our Discord server!
https://discord.gg/4nWK9mf
`
  console.log(splash)
}

configureHooks(router, store)

const isValidBrowser = supportedBrowsers.test(navigator.userAgent)

if (productionMode && isValidBrowser) {
  // noinspection TypeScriptValidateJSTypes
  init({
    app,
    dsn: "https://8efd301a6c794f3e9a84e741edef2cfe@sentry.io/1406820",
    release: process.env.__COMMIT_HASH__,
    ignoreErrors: [
      "ResizeObserver loop limit exceeded",
      "ResizeObserver loop completed with undelivered notifications.",
    ],
    integrations: [browserTracingIntegration({ router }), replayIntegration()],
    replaysOnErrorSampleRate: 0.05,
    tracesSampleRate: 0.05,
  })
} else if (process.env.NODE_ENV === "production") {
  console.log("Unsupported browser. Automatic error reports will not be sent.")
}

window.artconomy = app.mount("#app")
