// Probably need to eliminate this once it's refactored, since it's only ever used one place and most of its
// functionality is in modules now.
import {artCall, NOTIFICATION_MAPPING} from '@/lib/lib'
import Viewer from '@/mixins/viewer'
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import {SingleController} from '@/store/singles/controller'
import AcNotification from '@/types/AcNotification'
import {ListController} from '@/store/lists/controller'

@Component
export default class NotificationsListBase extends mixins(Viewer) {
  @Prop({default: true})
  public autoRead!: boolean

  @Prop({required: true})
  public subset!: string

  public notifications: ListController<
    AcNotification<any, any>> = null as unknown as ListController<AcNotification<any, any>>

  public toMark: Array<Partial<AcNotification<any, any>>> = []
  public marking: Array<Partial<AcNotification<any, any>>> = []
  public marked: Array<Partial<AcNotification<any, any>>> = []
  public readUrl = '/api/profiles/v1/data/notifications/mark-read/'
  public loopId: number = 0

  // noinspection JSMethodCanBeStatic
  public dynamicComponent(type: number): string {
    return NOTIFICATION_MAPPING[type]
  }

  public clickRead(notification: SingleController<AcNotification<any, any>>) {
    if (this.autoRead) {
      return
    }
    notification.updateX({read: true})
    artCall({
      url: '/api/profiles/v1/data/notifications/mark-read/',
      method: 'patch',
      data: [{id: (notification.x as AcNotification<any, any>).id, read: true}],
    },
    ).then(this.sendUpdateEvent)
  }

  public markRead(controller: SingleController<AcNotification<any, any>>) {
    const notification = controller.x as AcNotification<any, any>
    if (!this.autoRead) {
      return () => undefined
    }
    return () => {
      const self = this
      if (notification.read) {
        return
      }
      if (this.toMarkIDs.indexOf(notification.id) !== -1) {
        return
      }
      if (this.markedIDs.indexOf(notification.id) !== -1) {
        return
      }
      self.toMark.push({id: notification.id, read: true})
    }
  }

  public clearMarking() {
    // In case of failure, allow to try again.
    this.marking = []
  }

  public sendUpdateEvent() {
    this.$store.dispatch('notifications/runFetch').then()
  }

  public postMark() {
    for (const notification of this.marking) {
      const index = this.toMark.indexOf(notification)
      if (index > -1) {
        this.toMark.splice(index, 1)
        this.marked.push(notification)
      }
    }
    this.clearMarking()
    this.sendUpdateEvent()
  }

  public readMonitor() {
    if (this.toMark.length && !this.marking.length) {
      this.marking = this.toMark
      artCall(
        {url: this.readUrl, method: 'patch', data: this.marking},
      ).then(this.postMark).catch(this.clearMarking)
    }
  }

  public get toMarkIDs() {
    return this.toMark.map((x) => x.id)
  }

  public get markedIDs() {
    return this.marked.map((x) => x.id)
  }

  public destroyed() {
    this.readMonitor()
    window.clearInterval(this.loopId)
  }

  public created() {
    this.notifications = this.$getList(this.subset + 'Notifications')
    this.loopId = window.setInterval(this.readMonitor, 3000)
  }
}
