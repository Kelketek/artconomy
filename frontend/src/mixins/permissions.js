// This mixin can only be used on views that have a definitive controlling user,
// such as a user's profile or settings page. The username must be in the route params.
export default {
  data: function () {
    return {
      user: {username: this.$route.params.username}
    }
  },
  created () {
    this.$root.setUser(this.user.username, this)
  },
  computed: {
    controls: function () {
      return this.viewer.is_staff || (this.user.username === this.viewer.username)
    },
    viewer: function () {
      return this.$root.user
    }
  }
}
