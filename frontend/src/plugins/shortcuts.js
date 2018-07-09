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
          return this.$displayImage(asset, thumbName)
        },
        $displayImage (asset, thumbName) {
          if (['gallery', 'full', 'preview'].indexOf(thumbName) === -1) {
            if (asset.preview) {
              return asset.preview.thumbnail
            }
          }
          return asset.file[thumbName]
        }
      }
    })
  }
}
