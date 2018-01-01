// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import moment from 'moment'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import VueFormGenerator from 'vue-form-generator'
import 'vue-form-generator/dist/vfg.css'  // optional full css additions
import { $, jQuery } from 'jquery'
import BootstrapVue from 'bootstrap-vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App'
import NavBar from './components/NavBar'
import fieldCharacterSearch from './components/fieldCharacterSearch'
import { artCall, md } from './lib'
import {ErrorHandler} from './plugins/error'
import {router} from './router'

// export for others scripts to use
window.$ = $
window.jQuery = jQuery

let CACHE_TIMEOUT = 1800

Vue.use(VueRouter)
Vue.use(BootstrapVue)
Vue.use(VueFormGenerator)
Vue.use(ErrorHandler)
Vue.config.productionTip = false
Vue.component('ac-navbar', NavBar)
Vue.component('fieldCharacterSearch', fieldCharacterSearch)

/* eslint-disable no-new */
window.artconomy = new Vue({
  el: '#app',
  router,
  template: '<App :user="user"/>',
  components: {App, NavBar},
  data: {
    user: null,
    usercache: {},
    md: md,
    errorCode: null
  },
  methods: {
    log (data) {
      // eslint-disable-next-line
      console.log(data)
      return data
    },
    userSaver (target, response) {
      response.timestamp = moment.now()
      this.usercache[response.username] = response
      target.user = response
    },
    saveCachedUser (target) {
      let self = this
      return function (response) {
        self.userSaver(target, response)
      }
    },
    cacheUser (username, target) {
      artCall(`/api/profiles/v1/data/user/${username}/`, 'GET', undefined, this.saveCachedUser(target), this.$error)
    },
    setUser (username, target) {
      if (this.usercache[username]) {
        if (this.usercache[username].timestamp.seconds > CACHE_TIMEOUT) {
          this.cacheUser(username, target)
        } else {
          target.user = this.usercache[username]
        }
      } else {
        this.cacheUser(username, target)
      }
    },
    loadUser (loadProfile) {
      let self = this
      function loadLoggedIn (response) {
        self.userSaver(self, response)
        if (loadProfile) {
          self.$router.push({name: 'Profile', params: {username: self.user.username}})
        }
      }
      artCall('/api/profiles/v1/data/requester/', 'GET', undefined, loadLoggedIn)
    }
  },
  created () {
    this.loadUser()
  }
})
