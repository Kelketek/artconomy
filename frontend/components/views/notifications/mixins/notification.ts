import {toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import {computed, ComputedRef, defineComponent, PropType} from 'vue'
import AcNotification from '@/types/AcNotification.ts'
import {Asset} from '@/types/Asset.ts'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import {User} from '@/store/profiles/types/User.ts'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
import {useImg} from '@/plugins/shortcuts.ts'


export interface NotificationProps<T, D> {
  notification: AcNotification<T, D>,
}


export interface DisplayData {
  display: Asset,
}

export type NotificationUser = TerseUser & Asset

export interface DisplayUser {
  display: NotificationUser
}

export default defineComponent({
  // Not sure why, but toNative is not being respected here for typing, even though it works.
  mixins: [toNative(Viewer) as any],
  props: {notification: {type: Object as PropType<AcNotification<any, any>>, required: true}},
  computed: {
    event() {
      return this.notification.event
    },
  },
})

export const useEvent = <T, D>(props: NotificationProps<T, D>) => computed(() => props.notification.event)

// Workaround for the notifications image. Sometimes we use a user as the image reference, with their avatar URL.
export const useNotificationAvatar = (asset: Asset|TerseUser, viewer: ComputedRef<User|AnonUser>) => {
  if ((asset as TerseUser).avatar_url) {
    return computed(() => (asset as TerseUser).avatar_url)
  }
  return
}

