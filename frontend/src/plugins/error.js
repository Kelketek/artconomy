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
