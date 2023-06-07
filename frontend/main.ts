import 'intersection-observer'
import './artconomy.css'
import Vuetify from 'vuetify/lib'
import * as Sentry from '@sentry/browser'
import * as Integrations from '@sentry/integrations'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex'
import {createStore} from './store'
import App from './App.vue'
import {configureHooks, router} from './router'
import {FormControllers} from '@/store/forms/registry'
import {Shortcuts} from './plugins/shortcuts'
import Bowser from 'bowser'
import {Decimal} from 'decimal.js'
import {formatSize, genId} from './lib/lib'
import {Lists} from '@/store/lists/registry'
import {Singles} from '@/store/singles/registry'
import colors from 'vuetify/es5/util/colors'
import {Profiles} from '@/store/profiles/registry'
import {Characters} from '@/store/characters/registry'
import VueObserveVisibility from 'vue-observe-visibility'
import {VueSocket} from '@/plugins/socket'
import {User} from '@/store/profiles/types/User'
// eslint-disable-next-line import/no-duplicates
import '@stripe/stripe-js'
// eslint-disable-next-line import/no-duplicates
import {StripeConstructor, Stripe} from '@stripe/stripe-js'
import {PROCESSORS} from '@/types/PROCESSORS'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {VCol, VRow} from 'vuetify/lib/components'
import {AnonUser} from '@/store/profiles/types/AnonUser'

declare global {
  interface Window {
    artconomy: Vue,
    PRERENDERING: number,
    windowId: string,
    USER_PRELOAD: User|AnonUser,
    RECAPTCHA_SITE_KEY: string,
    STRIPE_PUBLIC_KEY: string,
    DEFAULT_CARD_PROCESSOR: PROCESSORS,
    DEFAULT_SERVICE_PLAN_NAME: string,
    Stripe?: StripeConstructor,
    StripeInstance: Stripe,
    _drip: () => void,
  }
}

Vue.use(VueRouter)
Vue.use(Vuex)
Vue.use(VueSocket, {endpoint: `wss://${window.location.host}/ws/events/`})
Vue.use(Shortcuts)
Vue.use(Vuetify)
Vue.use(FormControllers)
Vue.use(Lists)
Vue.use(Singles)
Vue.use(Characters)
Vue.use(Profiles)
Vue.use(VueObserveVisibility)
Vue.component('VCol', VCol)
Vue.component('VRow', VRow)
Vue.config.productionTip = false

Vue.filter('formatSize', formatSize)

// @ts-ignore
window.Decimal = Decimal
// The 'window ID' is used to distinguish one tab from another when making requests to the server. This is useful for
// some websocket activities where one tab is the originator of a change and others need to pick it up.
window.windowId = genId()

const browser = Bowser.getParser(window.navigator.userAgent)
const isValidBrowser = browser.satisfies({
  chrome: '>=100',
  firefox: '>=100',
  opera: '>=90',
  safari: '>=15',
  edge: '>=100',
})

const productionMode = process.env.NODE_ENV === 'production'

if (productionMode && isValidBrowser) {
  // noinspection TypeScriptValidateJSTypes
  Sentry.init({
    dsn: 'https://8efd301a6c794f3e9a84e741edef2cfe@sentry.io/1406820',
    // @ts-ignore
    release: __COMMIT_HASH__,
    ignoreErrors: [
      'ResizeObserver loop limit exceeded', 'ResizeObserver loop completed with undelivered notifications.',
    ],
    integrations: [new (Integrations as any).Vue({
      Vue,
      attachProps: true,
    })],
  })
} else if (process.env.NODE_ENV === 'production') {
  console.log('Unsupported browser. Automatic error reports will not be sent.')
} else {
  // Ignore image loading errors.
  const ogError = console.error
  console.error = (message: any) => {
    const converted = message + ''
    if (converted.startsWith('[Vuetify] Image load failed')) {
      return
    }
    ogError(message)
  }
}

if (productionMode) {
  const splash = `
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%      %%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%           %%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%             %%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%               %%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%                %%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%         %       %%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%         %%        %%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%         %%%        %%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%         %%%%%       %%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        %%%%%%        %%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        %%%%%%%%       %%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%        %%%%%%%%%        %%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%        %%%%%%%%%%       %%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%    #                            %%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%                                  %%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%               /%%%%%       %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%       ,%%%%%%%%%%%%%%%      *%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%.      %%%%%%%%%%%%%%%%%      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%      %%%%%%%%%%%%%%%%%%      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%     %%%%%%%%%%%%%%%%%%%%     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%  %%%%%%%%%%%%%%%%%%%%%%%%   %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 

!!!WARNING!!! This is for advanced users. DO NOT paste anything you don't understand into this console. If you do,
your account security could be at risk!

If you DO know how to use this console, please geek out with us in the #tech-nerd-zone channel on our Discord server!
https://discord.gg/4nWK9mf
`
  console.log(splash)
}

const vuetifySettings = {
  icons: {
    iconfont: 'mdiSvg',
  },
  theme: {
    dark: true,
    themes: {
      dark: {
        primary: colors.blue.darken2,
        secondary: colors.purple,
        danger: colors.red,
        darkBase: colors.grey,
      },
    },
  },
  options: {
    customProperties: true,
  },
}

const store = createStore()
configureHooks(router, store)

window.artconomy = new Vue({
  el: '#app',
  router,
  store,
  render: (h) => h(App),
  // @ts-ignore
  vuetify: new Vuetify(vuetifySettings),
  components: {App},
})

window.artconomy.$mount('#app')
