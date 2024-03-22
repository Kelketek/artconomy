import {Component} from 'vue-facing-decorator'
import {
  ArtVue,



} from '@/lib/lib.ts'
import {User} from '@/store/profiles/types/User.ts'
import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'
import {
  deriveDisplayName, formatDate,
  formatDateTerse, formatDateTime,
  formatSize,
  guestName,
  truncateText,
} from '@/lib/otherFormatters.ts'
import {profileLink} from '@/lib/otherFormatters.ts'
import {md, textualize} from '@/lib/markdown.ts'

@Component
export default class Formatting extends ArtVue {
  // noinspection JSMethodCanBeStatic
  public mdRender(text: string): string {
    return md.render(text)
  }

  // noinspection JSMethodCanBeStatic
  public mdRenderInline(text: string): string {
    return md.renderInline(text)
  }

  // noinspection JSMethodCanBeStatic
  public truncateText(text: string, maxLength: number) {
    return truncateText(text, maxLength)
  }

  // noinspection JSMethodCanBeStatic
  public formatDate(dateString: string) {
    return formatDate(dateString)
  }

  // noinspection JSMethodCanBeStatic
  public formatDateTerse(dateString: string) {
    return formatDateTerse(dateString)
  }

  // noinspection JSMethodCanBeStatic
  public formatDateTime(dateString: string) {
    return formatDateTime(dateString)
  }

  public textualize(markdownString: string) {
    return textualize(markdownString)
  }

  public deriveDisplayName(username: string) {
    return deriveDisplayName(username)
  }

  public guestName(username: string) {
    return guestName(username)
  }

  public profileLink(user: User|RelatedUser|null) {
    return profileLink(user)
  }

  public formatSize(num: number) {
    return formatSize(num)
  }
}
