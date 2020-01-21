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
import Big from 'big.js'
import * as lineItemFunctions from '@/lib/lineItemFunctions'
// import './registerServiceWorker'
import {formatSize} from './lib/lib'
import {Lists} from '@/store/lists/registry'
import {Singles} from '@/store/singles/registry'
import colors from 'vuetify/es5/util/colors'
import {Profiles} from '@/store/profiles/registry'
import {Characters} from '@/store/characters/registry'
import VueObserveVisibility from 'vue-observe-visibility'
import {genLineItem} from '@/lib/specs/helpers'

declare global {
  interface Window {
    artconomy: Vue,
    PRERENDERING: number,
  }
}

Vue.use(VueRouter)
Vue.use(Vuex)
Vue.use(Shortcuts)
Vue.use(Vuetify)
Vue.use(FormControllers)
Vue.use(Lists)
Vue.use(Singles)
Vue.use(Characters)
Vue.use(Profiles)
Vue.use(VueObserveVisibility)
Vue.config.productionTip = false

Vue.filter('formatSize', formatSize)

Big.DP = 2
Big.RM = 2
// @ts-ignore
window.Big = Big

const browser = Bowser.getParser(window.navigator.userAgent)
const isValidBrowser = browser.satisfies({
  chrome: '>=70',
  firefox: '>=68.3',
  opera: '>=22',
  safari: '>=12',
  edge: '>=16',
})

const productionMode = process.env.NODE_ENV === 'production'

if (productionMode && isValidBrowser) {
  // noinspection TypeScriptValidateJSTypes
  Sentry.init({
    dsn: 'https://8efd301a6c794f3e9a84e741edef2cfe@sentry.io/1406820',
    // @ts-ignore
    release: __COMMIT_HASH__,
    integrations: [new (Integrations as any).Vue({
      Vue,
      attachProps: true,
    })],
  })
} else if (process.env.NODE_ENV === 'production') {
  console.log('Unsupported browser. Automatic error reports will not be sent.')
}

const vuetifySettings = {
  icons: {
    iconfont: 'mdiSvg',
  },
  theme: {
    dark: true,
    themes: {
      dark: {
        primary: colors.blue,
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
  components: {App}, // , NavBar},
})

window.artconomy.$mount('#app')
// @ts-ignore
window.lines = lineItemFunctions
// @ts-ignore
window.genLineItem = genLineItem
