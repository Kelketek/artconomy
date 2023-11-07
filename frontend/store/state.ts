import {ListState} from '@/store/lists/types/ListState'
import {SingleState} from '@/store/singles/types/SingleState'
import {FormState} from '@/store/forms/types/FormState'
import {ProfileState} from '@/store/profiles/types/ProfileState'
import {NotificationsState} from '@/store/notifications/types/NotificationsState'
import {ErrorState} from '@/store/errors/types'
import {ContentRating} from '@/types/ContentRating'

export enum AlertCategory {
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info',
}

export interface Alert {
  id?: string,
  message: string,
  timeout: number,
  category: AlertCategory
}

export interface State {
  projectName: string,
  showSupport: boolean,
  markdownHelp: boolean,
  uploadVisible: boolean,
  iFrame: boolean,
  searchInitialized: boolean,
  alerts: Alert[],
  ageAsked: boolean,
  contentRating: ContentRating,
  showAgeVerification: boolean,
  showCookieDialog: boolean,
  notifications?: NotificationsState,
  errors?: ErrorState,
  lists?: {[key: string]: ListState<any>},
  singles?: {[key: string]: SingleState<any>},
  forms?: {[key: string]: FormState},
  profiles?: {
    viewerRawUsername: string,
    users: {[key: string]: ProfileState},
  },
}
