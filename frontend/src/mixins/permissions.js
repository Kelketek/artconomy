// This mixin can only be used on views that have a definitive controlling user,
// such as a user's profile or settings page. The username must be in the route params.
export default {
  data: function () {
    return {
      user: {username: this.$route.params.username}
    }
  },
  created () {
    this.configureUser()
  },
  methods: {
    configureUser () {
      this.$root.setUser(this.user.username, this)
    },
    refreshUser () {
      delete this.$root.usercache[this.user.username]
      this.configureUser()
    }
  },
  computed: {
    controls: function () {
      return this.viewer.is_staff || (this.user.username === this.viewer.username)
    },
    is_current: function () {
      return this.user.username === this.viewer.username
    }
  }
}
