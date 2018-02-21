export const Shortcuts = {
  install (Vue) {
    Vue.mixin({
      methods: {
        $go (route) {
          this.$router.history.push(route)
        },
        $img (asset, thumbName) {
          if (!asset) {
            return '/static/images/default-avatar.png'
          }
          return asset.file[thumbName]
        }
      }
    })
  }
}
