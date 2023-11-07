import {AxiosError} from 'axios'

export type AcServerError = AxiosError<{detail: any} | Record<string, string[]>>
