import {Component, mixins, Prop} from 'vue-facing-decorator'
import {Asset} from '@/types/Asset.ts'
import {extPreview, RATINGS, thumbFromSpec} from '@/lib/lib.ts'
import Viewer, {useViewer} from './viewer.ts'
import {User} from '@/store/profiles/types/User.ts'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
import {computed} from 'vue'
import {ContentRating} from '@/types/ContentRating.ts'


// Deprecated.
@Component
export default class AssetBase extends mixins(Viewer) {
  // Define in child.
  declare asset: Asset|null
  // Define in child.
  declare thumbName: string
  @Prop({default: false})
  public compact!: boolean

  @Prop({default: false})
  public terse!: boolean

  @Prop({default: false})
  public popOut!: boolean

  @Prop()
  public contain!: string

  @Prop({default: '/static/images/default-avatar.png'})
  public fallbackImage!: string

  public get ratingText() {
    return getRatingText(this.asset)
  }

  public get tags() {
    return getTags(this.asset)
  }

  public get displayImage() {
    return getDisplayImage(this.asset, this.thumbName, this.isImage, this.fallbackImage)
  }

  public get blacklisted() {
    return getBlackListed(this.asset, this.tags, this.viewer as User|AnonUser)
  }

  public get nsfwBlacklisted() {
    return getNsfwBlacklisted(this.asset, this.tags, this.assetRating, this.viewer as User|AnonUser)
  }

  public get assetRating() {
    return getAssetRating(this.asset)
  }

  public get permittedRating() {
    return getPermittedRating(this.asset, this.rating)
  }

  public get isImage() {
    return getIsImage(this.asset)
  }

  public get nerfed() {
    return getNerfed(this.rating, this.viewer as User|AnonUser)
  }

  public get canDisplay() {
    return getCanDisplay(this.permittedRating, this.blacklisted, this.nsfwBlacklisted)
  }
}

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

//   @Prop({default: false})
//   public compact!: boolean
//
//   @Prop({default: false})
//   public terse!: boolean
//
//   @Prop({default: false})
//   public popOut!: boolean
//
//   @Prop()
//   public contain!: string
//
//   @Prop({default: '/static/images/default-avatar.png'})
//   public fallbackImage!: string

export const assetDefaults = () => ({
  compact: false,
  terse: false,
  popOut: false,
  fallBackImage: '/static/images/default-avatar.png',
})
