import {Ratings} from '@/types/enums/Ratings.ts'
import {thumbFromSpec} from '@/mixins/asset_base.ts'
import {computed, ComputedRef} from 'vue'

import type {Asset} from '@/types/main'

export const useSharable = (shareMedia: ComputedRef<Asset|null>) => {
  const shareMediaUrl = computed(() => (shareMedia.value && thumbFromSpec('gallery', shareMedia.value.file)) || '')
  const shareMediaClean = computed(() => shareMedia.value && shareMedia.value.rating === Ratings.GENERAL)
  return {shareMediaUrl, shareMediaClean}
}
