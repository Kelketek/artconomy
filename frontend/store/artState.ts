import {ListState} from '@/store/lists/types/ListState.ts'
import {SingleState} from '@/store/singles/types/SingleState.ts'
import {FormState} from '@/store/forms/types/FormState.ts'
import {ProfileState} from '@/store/profiles/types/ProfileState.ts'
import {NotificationsState} from '@/store/notifications/types/NotificationsState.ts'
import {ErrorState} from '@/store/errors/types.ts'
import {ContentRating} from '@/types/ContentRating.ts'

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

export interface ArtState {
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
