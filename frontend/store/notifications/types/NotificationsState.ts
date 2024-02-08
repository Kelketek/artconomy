import {NotificationStats} from '@/store/notifications/types/NotificationStats.ts'

export interface NotificationsState {
  stats: NotificationStats,
  loopID: number
}
