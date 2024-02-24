import './artconomy.css'
import * as Sentry from '@sentry/vue'
import {createApp, defineAsyncComponent, h} from 'vue'
import {createStore} from './store/index.ts'
const App = defineAsyncComponent(() => import('./App.vue'))
import VueMask from '@devindex/vue-mask'
import {configureHooks, router} from '@/router/index.ts'
import {createForms} from '@/store/forms/registry.ts'
import {Shortcuts} from './plugins/shortcuts.ts'
import supportedBrowsers from './supportedBrowsers.ts'
import {genId} from './lib/lib.ts'
import {createLists} from '@/store/lists/registry.ts'
import {createSingles} from '@/store/singles/registry.ts'
import {createProfiles} from '@/store/profiles/registry.ts'
import {createCharacters} from '@/store/characters/registry.ts'
import VueObserveVisibility from 'vue-observe-visibility'
import {createVueSocket} from '@/plugins/socket.ts'
import {createVuetify} from '@/plugins/vuetify.ts'
import {User} from '@/store/profiles/types/User.ts'
import '@stripe/stripe-js'
import {Stripe, StripeConstructor} from '@stripe/stripe-js'
import {PROCESSORS} from '@/types/PROCESSORS.ts'
import {VCol, VRow} from 'vuetify/lib/components/VGrid/index.mjs'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
const AcComment = defineAsyncComponent(() => import('@/components/comments/AcComment.vue'))
const AcCommentSection = defineAsyncComponent(() => import('@/components/comments/AcCommentSection.vue'))
import {createTargetsPlugin} from '@/plugins/targets.ts'
import {createRegistries} from '@/plugins/createRegistries.ts'

declare global {
  interface Window {
    // We shouldn't be referencing this directly anywhere.
    // We use it during debugging.
    artconomy: any,
    chrome?: boolean,
    PRERENDERING: number,
    windowId: string,
    USER_PRELOAD: User|AnonUser,
    SANDBOX_APIS: boolean,
    RECAPTCHA_SITE_KEY: string,
    STRIPE_PUBLIC_KEY: string,
    DEFAULT_CARD_PROCESSOR: PROCESSORS,
    DEFAULT_SERVICE_PLAN_NAME: string,
    Stripe?: StripeConstructor,
    StripeInstance: Stripe,
    _drip: () => void,
    _ga: () => void,
  }
}

const productionMode = process.env.NODE_ENV === 'production'

const app = createApp({
  render: () => h(App),
  components: {App, VCol, VRow},
})
const store = createStore()

app.use(router)
app.use(store)
app.use(VueMask)
app.use(createVueSocket({endpoint: `wss://${window.location.host}/ws/events/`}))
app.use(Shortcuts)
app.use(createVuetify())
app.use(createLists(store))
app.use(createForms(store))
app.use(createSingles(store))
app.use(createCharacters(store))
app.use(createProfiles(store))
app.use(createRegistries())
app.use(createTargetsPlugin(false))
app.use(VueObserveVisibility)
// Needed because these tags are inter-referential
app.component('AcComment', AcComment)
app.component('AcCommentSection', AcCommentSection)


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
  Sentry.init({
    app,
    dsn: 'https://8efd301a6c794f3e9a84e741edef2cfe@sentry.io/1406820',
    // @ts-ignore
    release: process.env.__COMMIT_HASH__,
    ignoreErrors: [
      'ResizeObserver loop limit exceeded', 'ResizeObserver loop completed with undelivered notifications.',
    ],
    integrations: [
      new Sentry.BrowserTracing({
        routingInstrumentation: Sentry.vueRouterInstrumentation(router),
      }),
      new Sentry.Replay(),
    ],
    tracesSampleRate: .05,
  })
} else if (process.env.NODE_ENV === 'production') {
  console.log('Unsupported browser. Automatic error reports will not be sent.')
}

window.artconomy = app.mount('#app')
