import {extPreview, getExt, isImage} from '@/lib'
import _Vue from 'vue'
import {Ratings} from '@/store/profiles/types/Ratings'
// TODO: Declaration file? Not sure why this doesn't exist already, considering the lib.
// @ts-ignore
import goTo from 'vuetify/es5/services/goto'

declare module 'vue/types/vue' {
  // Global properties can be declared
  // on the `VueConstructor` interface
  interface Vue {
    $displayImage: (asset: object, thumbName: string) => string,
    $img: (asset: object|null, thumbName: string, fallback?: boolean) => string,
    $goTo: (target: any) => void,
  }
}

declare interface Asset {
  rating: Ratings,
  file: null | { [key: string]: string }
  preview: null | { [key: string]: string }
}

// Super hacky place to put this so it can be mocked out. Side-steps Jest's unbearable module mocker.
export const goToNameSpace = {
  goTo(target: any) {
    goTo(target)
  },
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
      $goTo(target: any) {
        goToNameSpace.goTo(target)
      },
    },
  })
}
