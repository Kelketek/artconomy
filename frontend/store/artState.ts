import {ErrorState} from '@/store/errors/types.ts'
import type {SingleState} from '@/store/singles/types.d.ts'
import {ProfileState} from '@/store/profiles/types/main'
import {RatingsValue} from '@/types/main'
import type {ListState} from '@/store/lists/types.d.ts'
import {FormState} from '@/store/forms/types/main'

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
