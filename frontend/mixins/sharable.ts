import {Ratings} from '@/types/enums/Ratings.ts'
import {defaultFallbackImage, thumbFromSpec} from '@/mixins/asset_base.ts'
import {computed, ComputedRef} from 'vue'

import type {Asset} from '@/types/main'

export const useSharable = (shareMedia: ComputedRef<Asset|null>) => {
  const shareMediaUrl = computed(() => (shareMedia.value && thumbFromSpec('gallery', shareMedia.value.file, defaultFallbackImage)) || '')
  const shareMediaClean = computed(() => shareMedia.value && shareMedia.value.rating === Ratings.GENERAL)
  return {shareMediaUrl, shareMediaClean}
}
