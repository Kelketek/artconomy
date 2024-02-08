import {extPreview, getExt, isImage} from '@/lib/lib.ts'
import {createApp} from 'vue'
import {Asset} from '@/types/Asset.ts'
import {v4 as uuidv4} from 'uuid'

export function Shortcuts(app: ReturnType<typeof createApp>): void {
  app.mixin({
    // eslint-disable-next-line vue/no-reserved-keys
    data: () => ({_uid: uuidv4()}),
    methods: {
      $img(asset: Asset, thumbName: string, fallback: boolean) {
        if (!asset || !asset.file) {
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
      $goTo(selector: string) {
        const target = document.querySelector(selector)
        if (!target) {
          console.error(`Could not find target for selector ${selector}`)
          return
        }
        target.scrollIntoView()
      },
      $displayImage(asset: Asset, thumbName: string) {
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
