import {ListState} from '@/store/lists/types/ListState.ts'
import {SingleState} from '@/store/singles/types/SingleState.ts'
import {FormState} from '@/store/forms/types/FormState.ts'
import {ProfileState} from '@/store/profiles/types/ProfileState.ts'
import {ErrorState} from '@/store/errors/types.ts'
import {RatingsValue} from '@/types/Ratings.ts'

export const AlertCategory = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
} as const

export type AlertCategoryKey = typeof AlertCategory[keyof typeof AlertCategory]

export interface Alert {
  id?: string,
  message: string,
  timeout: number,
  category: AlertCategoryKey,
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
  contentRating: RatingsValue,
  showAgeVerification: boolean,
  showCookieDialog: boolean,
  messagesOpen: boolean,
  errors?: ErrorState,
  lists?: {[key: string]: ListState<any>},
  singles?: {[key: string]: SingleState<any>},
  forms?: {[key: string]: FormState},
  profiles?: {
    viewerRawUsername: string,
    users: {[key: string]: ProfileState},
  },
}
