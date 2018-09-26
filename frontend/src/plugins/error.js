export const ErrorHandler = {
  install (Vue) {
    Vue.mixin({
      created () {
        this.$root.errorCode = null
      },
      methods: {
        $error (error) {
          this.$root.errorCode = error.status
        }
      },
      computed: {
        errorLogo () {
          if ([500, 503, 400, 404, 403].indexOf(this.$root.errorCode) !== -1) {
            return `/static/images/${this.$root.errorCode}.png`
          } else {
            return `/static/images/generic-error.png`
          }
        }
      }
    })
  },
  clearError (to, from, next) {
    if (window.artconomy) {
      window.artconomy.errorCode = null
    }
    next()
  }
}
