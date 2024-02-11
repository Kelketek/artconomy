import {Asset} from '@/types/Asset.ts'
import {extPreview, RATINGS, thumbFromSpec} from '@/lib/lib.ts'
import {useViewer} from './viewer.ts'
import {User} from '@/store/profiles/types/User.ts'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
import {computed} from 'vue'
import {ContentRating} from '@/types/ContentRating.ts'

const getRatingText = (asset: Asset|null) => {
  if (!asset) {
    return ''
  }
  return RATINGS[asset.rating]
}

const getTags = (asset: Asset | null): string[] => {
  return (asset && asset.tags) || []
}

const getDisplayImage = (asset: Asset|null, thumbName: string, isImage: boolean, fallbackImage: string) => {
  if (!(asset && asset.file)) {
    return fallbackImage
  }
  if (['gallery', 'full', 'preview'].indexOf(thumbName) === -1) {
    if (asset.preview) {
      return thumbFromSpec('thumbnail', asset.preview)
    }
  }
  if (!isImage) {
    return extPreview(asset.file.full)
  }
  return thumbFromSpec(thumbName, asset.file)
}

const getIsImage = (asset: Asset|null) => {
  if (!(asset && asset.file)) {
    // We'll be returning a default image value.
    return true
  }
  return (['data:image', 'svg'].indexOf(asset.file.__type__) !== -1)
}

const getBlackListed = (asset: Asset|null, tags: string[], viewer: User|AnonUser) => {
  if (!asset) {
    return []
  }
  return tags.filter((n) => viewer.blacklist.includes(n))
}

const getNsfwBlacklisted = (asset: Asset|null, tags: string[], assetRating: ContentRating, viewer: User|AnonUser) => {
  if (!asset) {
    return []
  }
  if (!assetRating) {
    return []
  }
  return tags.filter((n) => viewer.nsfw_blacklist.includes(n))
}

const getAssetRating = (asset: Asset|null): ContentRating => {
  if (!asset) {
    return 0
  }
  return asset.rating
}

const getPermittedRating = (asset: Asset|null, viewerRating: ContentRating) => {
  if (!asset) {
    return true
  }
  return asset.rating <= viewerRating
}

const getNerfed = (rating: ContentRating, viewer: User|AnonUser) => {
  return viewer.rating && (rating < viewer.rating)
}

const getCanDisplay = (permittedRating: boolean, blacklisted: string[], nsfwBlacklisted: string[]) => {
  if (permittedRating) {
    if (!blacklisted.length && !nsfwBlacklisted.length) {
      return true
    }
  }
  return false
}

export const useAssetHelpers = ({asset, thumbName, fallbackImage}: {asset: Asset|null, thumbName: string, fallbackImage: string}) => {
  const {viewer, rating} = useViewer()
  const isImage = computed(() => getIsImage(asset))
  const displayImage = computed(() => getDisplayImage(asset, thumbName, isImage.value, fallbackImage))
  const ratingText = computed(() => getRatingText(asset))
  const tags = computed(() => getTags(asset))
  const assetRating = computed(() => getAssetRating(asset))
  const blacklisted = computed(() => getBlackListed(asset, tags.value, viewer.value))
  const nsfwBlacklisted = computed(() => getNsfwBlacklisted(asset, tags.value, assetRating.value, viewer.value))
  const permittedRating = computed(() => getPermittedRating(asset, rating.value))
  const nerfed = computed(() => getNerfed(rating.value, viewer.value))
  const canDisplay = computed(() => getCanDisplay(permittedRating.value, blacklisted.value, nsfwBlacklisted.value))
  return {
    isImage,
    displayImage,
    ratingText,
    tags,
    assetRating,
    blacklisted,
    nsfwBlacklisted,
    permittedRating,
    nerfed,
    canDisplay,
  }
}

export const assetDefaults = () => ({
  compact: false,
  terse: false,
  popOut: false,
  contain: false,
  fallbackImage: '/static/images/default-avatar.png',
})
