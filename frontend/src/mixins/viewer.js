// This module should no longer be needed since we're now using the UserHandler plugin.
export default {
  computed: {
    rating: function () {
      let contentRating = 0
      if (this.viewer.sfw_mode) {
        return contentRating
      } else {
        return this.viewer.rating || 0
      }
    },
    viewer: function () {
      return this.$root.user
    }
  }
}
