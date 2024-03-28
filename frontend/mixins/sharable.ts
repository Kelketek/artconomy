import {ArtVue} from '@/lib/lib.ts'
import {Ratings} from '@/store/profiles/types/Ratings.ts'
import FileSpec from '@/types/FileSpec.ts'
import {Component} from 'vue-facing-decorator'
import {thumbFromSpec} from '@/mixins/asset_base.ts'
import {computed, ComputedRef} from 'vue'
import {Asset} from '@/types/Asset.ts'

@Component
export default class Sharable extends ArtVue {
  /* istanbul ignore next */
  public get shareMedia(): null|{file: FileSpec, rating: Ratings} {
    return null
  }

  public get shareMediaUrl() {
    return (this.shareMedia && thumbFromSpec('gallery', this.shareMedia.file)) || ''
  }

  public get shareMediaClean() {
    return this.shareMedia && this.shareMedia.rating === Ratings.GENERAL
  }
}

export const useSharable = (shareMedia: ComputedRef<Asset|null>) => {
  const shareMediaUrl = computed(() => (shareMedia.value && thumbFromSpec('gallery', shareMedia.value.file)) || '')
  const shareMediaClean = computed(() => shareMedia.value && shareMedia.value.rating === Ratings.GENERAL)
  return {shareMediaUrl, shareMediaClean}
}
