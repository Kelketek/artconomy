export default {
  computed: {
    rating: function () {
      let rating = 0
      if (this.viewer.sfw_mode) {
        return rating
      } else {
        return this.viewer.rating
      }
    },
    viewer: function () {
      return this.$root.user
    }
  }
}
