// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import VueFormGenerator from 'vue-form-generator'
import 'vuetify/dist/vuetify.min.css'
import './artconomy.css'
import { $, jQuery } from 'jquery'
import Vuetify from 'vuetify'
import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App'
import NavBar from './components/NavBar'
import fieldCharacterSearch from './components/fields/fieldCharacterSearch'
import fieldUserSearch from './components/fields/fieldUserSearch'
import fieldTagSearch from './components/fields/fieldTagSearch'
import fieldRecaptcha from './components/fields/fieldRecaptcha'
import fieldVText from './components/fields/fieldVText'
import fieldVCheckbox from './components/fields/fieldVCheckbox'
import fieldVSelect from './components/fields/fieldVSelect'
import fieldVFileUpload from './components/fields/fieldVFileUpload'
import fieldVColor from './components/fields/fieldVColor'
import { md, formatSize } from './lib'
import {ErrorHandler} from './plugins/error'
import {router} from './router'
import { UserHandler } from './plugins/user'
import { Timer } from './plugins/timer'
import { Shortcuts } from './plugins/shortcuts'

// export for others scripts to use
window.$ = $
window.jQuery = jQuery

Vue.use(VueRouter)
Vue.use(UserHandler)
Vue.use(VueFormGenerator)
Vue.use(ErrorHandler)
Vue.use(Timer)
Vue.use(Shortcuts)
Vue.use(Vuetify)
Vue.config.productionTip = false
Vue.component('fieldCharacterSearch', fieldCharacterSearch)
Vue.component('fieldUserSearch', fieldUserSearch)
Vue.component('fieldTagSearch', fieldTagSearch)
Vue.component('fieldRecaptcha', fieldRecaptcha)
Vue.component('fieldVText', fieldVText)
Vue.component('fieldVCheckbox', fieldVCheckbox)
Vue.component('fieldVSelect', fieldVSelect)
Vue.component('fieldVFileUpload', fieldVFileUpload)
Vue.component('fieldVColor', fieldVColor)

Vue.filter('formatSize', formatSize)

/* eslint-disable no-new */
window.artconomy = new Vue({
  el: '#app',
  router,
  template: '<App :user="user"/>',
  components: {App, NavBar},
  data: {
    userCache: {},
    md: md,
    $unread: 0,
    errorCode: null,
    fetchStarted: false
  },
  created () {
    this.$loadUser()
  },
  methods: {
    log (data) {
      // eslint-disable-next-line
      console.log(data)
      return data
    }
  }
})
