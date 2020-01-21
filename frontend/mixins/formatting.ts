import Component from 'vue-class-component'
import Vue from 'vue'
import {
  formatDate,
  formatDateTime,
  md,
  textualize,
  truncateText,
  formatDateTerse,
  deriveDisplayName,
  guestName,
  profileLink,
} from '@/lib'
import {User} from '@/store/profiles/types/User'

@Component
export default class Formatting extends Vue {
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
  public profileLink(user: User|null) {
    return profileLink(user)
  }
}
