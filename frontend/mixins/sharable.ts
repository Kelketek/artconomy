import {ArtVue, thumbFromSpec} from '@/lib/lib'
import {Ratings} from '@/store/profiles/types/Ratings'
import FileSpec from '@/types/FileSpec'
import {Component} from 'vue-facing-decorator'

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
