// This module should no longer be needed since we're now using the UserHandler plugin.
import moment from 'moment/moment'

export default {
  computed: {
    rating () {
      let contentRating = 0
      if (this.viewer.sfw_mode) {
        return contentRating
      } else {
        return this.viewer.rating || 0
      }
    },
    viewer () {
      if (this.$root.user === undefined) {
        // This can happen during testing.
        return null
      }
      return this.$root.user
    },
    isLoggedIn () {
      if (!this.viewer) {
        return false
      }
      if (this.viewer.username) {
        return true
      }
    },
    landscape () {
      if (!this.viewer) {
        return false
      }
      if (this.viewer.landscape_paid_through) {
        return moment(this.viewer.landscape_paid_through) >= moment.now()
      }
      return false
    },
    portrait () {
      if (!this.viewer) {
        return false
      }
      if (this.landscape) {
        return true
      }
      if (this.viewer.portrait_paid_through) {
        return moment(this.viewer.portrait_paid_through) >= moment.now()
      }
      return false
    }
  }
}
