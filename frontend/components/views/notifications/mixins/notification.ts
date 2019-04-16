import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import AcNotification from '@/types/AcNotification'
import Viewer from '@/mixins/viewer'

@Component
export default class NotificationMixin extends mixins(Viewer) {
  @Prop()
  public notification!: AcNotification<any, any>

  public get event() {
    return this.notification.event
  }
}
