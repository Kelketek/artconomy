export const Shortcuts = {
  install (Vue) {
    Vue.mixin({
      methods: {
        $go (route) {
          this.$router.history.push(route)
        },
        $img (asset, thumbName, fallback) {
          if (!asset) {
            return '/static/images/default-avatar.png'
          }
          if (asset.rating > this.rating) {
            if (fallback) {
              return '/static/images/default-avatar.png'
            }
            return ''
          }
          return asset.file[thumbName]
        }
      }
    })
  }
}
