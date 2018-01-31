// This mixin can only be used on views that have a definitive controlling user,
// such as a user's profile or settings page. The username must be in the route params.
export default {
  props: ['username'],
  data: function () {
    return {
      user: {username: this.username}
    }
  },
  created () {
    this.configureUser()
  },
  methods: {
    configureUser () {
      if (this.user.username === undefined) {
        // Some components are variably user-centric.
        return
      }
      this.$root.$setUser(this.user.username, this)
    },
    refreshUser () {
      delete this.$root.userCache[this.user.username]
      this.configureUser()
    }
  },
  computed: {
    controls: function () {
      if (this.user.username === undefined) {
        return false
      }
      return this.viewer.is_staff || (this.user.username === this.viewer.username)
    },
    is_current: function () {
      if (this.user.username === undefined) {
        return false
      }
      return this.user.username === this.viewer.username
    }
  },
  watch: {
    '$root.user': function (val) {
      if (val.username && this.user.username) {
        this.user = this.$root.user
      }
    }
  }
}
