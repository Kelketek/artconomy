import moment from 'moment/moment'
import { artCall } from '../lib'

let CACHE_TIMEOUT = 1800

export const UserHandler = {
  install (Vue) {
    Vue.mixin({
      data () {
        if (this.user === undefined) {
          return {
            user: null,
            userCache: this.$root.userCache || {}
          }
        }
        return {}
      },
      methods: {
        $userSaver (target, response) {
          response.timestamp = moment.now()
          this.$root.userCache[response.username] = response
          Vue.set(target, 'user', response)
        },
        $forceUser (userdata) {
          // Primarily for testing.
          if (userdata === null) {
            this.$root.user = null
            return
          }
          if (userdata.timestamp === undefined) {
            userdata.timestamp = moment.now()
          }
          if (userdata.username) {
            this.$root.userCache[userdata.username] = userdata
          }
          this.$root.user = userdata
        },
        $saveCachedUser (target) {
          let self = this
          return function (response) {
            self.$userSaver(target, response)
          }
        },
        $cacheUser (username, target) {
          artCall(`/api/profiles/v1/data/user/${username}/`, 'GET', undefined, this.$saveCachedUser(target), this.$error)
        },
        $setUser (username, target) {
          if (this.$root.userCache[username]) {
            if (this.$root.userCache[username].timestamp.seconds > CACHE_TIMEOUT) {
              this.$cacheUser(username, target)
            } else {
              target.user = this.$root.userCache[username]
            }
          } else {
            this.$cacheUser(username, target)
          }
        },
        $loadUser (loadProfile) {
          let self = this
          function loadLoggedIn (response) {
            self.$userSaver(self, response)
            if (loadProfile) {
              self.$router.push({name: 'Profile', params: {username: self.user.username}, query: {editing: true}})
            }
          }
          artCall('/api/profiles/v1/data/requester/', 'GET', undefined, loadLoggedIn, this.$error)
        }
      },
      computed: {
        viewer: function () {
          return this.$root.user
        },
        isLoggedIn () {
          return Boolean(this.$root.user.username)
        },
        rating: function () {
          let contentRating = 0
          if (this.viewer.sfw_mode) {
            return contentRating
          } else {
            return this.viewer.rating || 0
          }
        }
      }
    })
  }
}
