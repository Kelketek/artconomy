export const Shortcuts = {
  install (Vue) {
    Vue.mixin({
      methods: {
        $go (route) {
          this.$router.history.push(route)
        }
      }
    })
  }
}
