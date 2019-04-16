import {NotificationStats} from '@/store/notifications/types/NotificationStats'

export interface NotificationsState {
  stats: NotificationStats,
  loopID: number
}
