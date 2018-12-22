import {extPreview, getExt, isImage} from '../lib'

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
          if (getExt(asset.file.full) === 'SVG') {
            return asset.file.full
          }
          if (!isImage(asset.file.full)) {
            return extPreview(asset.file.full)
          }
          return asset.file[thumbName]
        }
      }
    })
  }
}
