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
  contentRating: number,
  showAgeVerification: boolean,
  showCookieDialog: boolean,
}
