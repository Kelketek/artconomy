import './artconomy.css'
// @ts-ignore
import * as Sentry from '@sentry/vue'
// @ts-ignore
import * as Integrations from '@sentry/integrations'
import {createApp, h} from 'vue'
import {createStore} from './store'
import App from './App.vue'
import VueMask from '@devindex/vue-mask'
import {configureHooks, router} from './router'
import {FormControllers} from '@/store/forms/registry'
import {Shortcuts} from './plugins/shortcuts'
import supportedBrowsers from './supportedBrowsers'
import {Decimal} from 'decimal.js'
import {genId} from './lib/lib'
import {Lists} from '@/store/lists/registry'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import {Characters} from '@/store/characters/registry'
import VueObserveVisibility from 'vue-observe-visibility'
import {createVueSocket} from '@/plugins/socket'
import {createVuetify} from '@/plugins/vuetify'
import {User} from '@/store/profiles/types/User'
import '@stripe/stripe-js'
import {Stripe, StripeConstructor} from '@stripe/stripe-js'
import {PROCESSORS} from '@/types/PROCESSORS'
import {VCol, VRow} from 'vuetify/lib/components/VGrid/index.mjs'
import {AnonUser} from '@/store/profiles/types/AnonUser'
import AcComment from '@/components/comments/AcComment.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import 'vite/modulepreload-polyfill';
import {createTargetsPlugin} from '@/plugins/targets'

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
app.use(Lists)
app.use(FormControllers)
app.use(Singles)
app.use(Characters)
app.use(Profiles)
app.use(createTargetsPlugin(false))
app.use(VueObserveVisibility)
app.component('AcComment', AcComment)
app.component('AcCommentSection', AcCommentSection)


window.artconomy = app

// @ts-ignore
window.Decimal = Decimal
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
