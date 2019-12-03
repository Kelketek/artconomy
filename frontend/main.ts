import 'intersection-observer'
import './artconomy.css'
import Vuetify from 'vuetify'
import 'vuetify/src/stylus/app.styl'
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
// import './registerServiceWorker'
import {formatSize} from './lib'
import {Lists} from '@/store/lists/registry'
import {Singles} from '@/store/singles/registry'
import colors from 'vuetify/es5/util/colors'
import {Profiles} from '@/store/profiles/registry'
import {Characters} from '@/store/characters/registry'
import VueObserveVisibility from 'vue-observe-visibility'

declare global {
  interface Window {
    artconomy: Vue,
    PRERENDERING: number,
  }
}

Vue.use(VueRouter)
Vue.use(Vuex)
Vue.use(Shortcuts)
Vue.use(Vuetify, {
  theme: {
    primary: colors.blue,
    secondary: colors.purple,
    danger: colors.red,
    darkBase: colors.grey,
  },
  options: {
    customProperties: true,
  },
})
Vue.use(FormControllers)
Vue.use(Lists)
Vue.use(Singles)
Vue.use(Characters)
Vue.use(Profiles)
Vue.use(VueObserveVisibility)
Vue.config.productionTip = false

Vue.filter('formatSize', formatSize)

if (process.env.NODE_ENV === 'production') {
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
}

const store = createStore()
configureHooks(router, store)

window.artconomy = new Vue({
  el: '#app',
  router,
  store,
  render: (h) => h(App),
  components: {App}, // , NavBar},
})

window.artconomy.$mount('#app')
