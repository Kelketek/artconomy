import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import {Asset} from '@/types/Asset'
import {extPreview, RATINGS, thumbFromSpec} from '@/lib/lib'
import Viewer from './viewer'
import {User} from '@/store/profiles/types/User'
import {AnonUser} from '@/store/profiles/types/AnonUser'

@Component
export default class AssetBase extends mixins(Viewer) {
  // Define in child.
  public asset!: Asset|null
  // Define in child.
  public thumbName!: string
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
    const asset = this.asset as Asset
    return RATINGS[asset.rating]
  }

  public get tags() {
    return (this.asset && this.asset.tags) || []
  }

  public get displayImage() {
    if (!(this.asset && this.asset.file)) {
      return this.fallbackImage
    }
    if (['gallery', 'full', 'preview'].indexOf(this.thumbName) === -1) {
      if (this.asset.preview) {
        return thumbFromSpec('thumbnail', this.asset.preview)
      }
    }
    if (!this.isImage) {
      return extPreview(this.asset.file.full)
    }
    return thumbFromSpec(this.thumbName, this.asset.file)
  }

  public get blacklisted() {
    if (!this.asset) {
      return []
    }
    const viewer = this.viewer as User|AnonUser
    return this.tags.filter((n) => viewer.blacklist.includes(n))
  }

  public get assetRating() {
    if (!this.asset) {
      return 0
    }
    return this.asset.rating
  }

  public get permittedRating() {
    if (!this.asset) {
      return true
    }
    return this.asset.rating <= this.rating
  }

  public get isImage() {
    if (!(this.asset && this.asset.file)) {
      // We'll be returning a default image value.
      return true
    }
    return (['data:image', 'svg'].indexOf(this.asset.file.__type__) !== -1)
  }

  public get nerfed() {
    const viewer = this.viewer as AnonUser
    return viewer.rating && (this.rating < viewer.rating)
  }

  public get canDisplay() {
    if (this.permittedRating) {
      if (!this.blacklisted.length) {
        return true
      }
    }
    return false
  }
}
