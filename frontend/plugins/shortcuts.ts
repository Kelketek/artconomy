import {extPreview, getExt, isImage} from '@/lib'
import _Vue from 'vue'
import {Ratings} from '@/store/profiles/types/Ratings'

declare module 'vue/types/vue' {
  // Global properties can be declared
  // on the `VueConstructor` interface
  interface Vue {
    $displayImage: (asset: object, thumbName: string) => string,
    $img: (asset: object, thumbName: string, fallback?: string) => string,
  }
}

declare interface Asset {
  rating: Ratings,
  file: null | { [key: string]: string }
  preview: null | { [key: string]: string }
}

export function Shortcuts(Vue: typeof _Vue): void {
  Vue.mixin({
    methods: {
      $img(asset, thumbName, fallback) {
        if (!asset) {
          return '/static/images/default-avatar.png'
        }
        // Viewer must be defined elsewhere. In near all cases, should be from the Viewer mixin.
        if (asset.rating > (this as any).viewer.rating) {
          if (fallback) {
            return '/static/images/default-avatar.png'
          }
          return ''
        }
        return this.$displayImage(asset, thumbName)
      },
      $displayImage(asset, thumbName) {
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
      },
    },
  })
}
