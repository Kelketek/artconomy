import {computed, ComputedRef} from 'vue'
import type {AcNotification, Asset, SubjectiveProps} from '@/types/main'
import {AnonUser, TerseUser, User} from '@/store/profiles/types/main'


export interface NotificationProps<T, D> extends SubjectiveProps {
  notification: AcNotification<T, D>,
}

export interface DisplayData<T extends Asset = Asset> {
  display: T,
}

export type NotificationUser = TerseUser & Asset

export interface DisplayUser {
  display: NotificationUser
}

export const useEvent = <T, D>(props: NotificationProps<T, D>) => computed(() => props.notification.event)

// Workaround for the notifications image. Sometimes we use a user as the image reference, with their avatar URL.
export const useNotificationAvatar = (asset: Asset|TerseUser, viewer: ComputedRef<User|AnonUser>) => {
  if ((asset as TerseUser).avatar_url) {
    return computed(() => (asset as TerseUser).avatar_url)
  }
  return
}

