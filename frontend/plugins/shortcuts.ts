import {computed, createApp} from 'vue'
import {Asset} from '@/types/Asset.ts'
import {v4 as uuidv4} from 'uuid'
import {extPreview, getExt, isImage} from '@/mixins/asset_base.ts'
import {useViewer} from '@/mixins/viewer.ts'
import type {RatingsValue} from '@/types/Ratings.ts'

export function Shortcuts(app: ReturnType<typeof createApp>): void {
  app.mixin({
    // eslint-disable-next-line vue/no-reserved-keys
    data: () => ({_uid: uuidv4()}),
    methods: {
    },
  })
}

export const deriveImage = (asset: Asset|null, thumbName: string, fallback: boolean, rating: RatingsValue) => {
  if (!asset || !asset.file) {
    return '/static/images/default-avatar.png'
  }
  // Viewer must be defined elsewhere. In near all cases, should be from the Viewer mixin.
  if (asset.rating > rating) {
    if (fallback) {
      return '/static/images/default-avatar.png'
    }
    return ''
  }
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

export const useImg = (asset: Asset, thumbName: string, fallback: boolean) => {
  const {rating} = useViewer()
  return computed(() => deriveImage(asset, thumbName, fallback, rating.value))
}
