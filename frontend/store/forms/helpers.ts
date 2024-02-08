import {AxiosError} from 'axios'
import {FormError} from '@/store/forms/types/FormError.ts'
import {FormErrorSet} from '@/store/forms/types/FormErrorSet.ts'

export function missingFieldError(errors: FormError): string[] {
  const result: string[] = []
  for (const key of Object.keys(errors)) {
    result.push(
      'Whoops! We had a coding error. Please contact support and tell them the following: ' +
      key + ': ' + errors[key].join(' '))
  }
  return result
}

const TRANSLATED: {[key: string]: string} = {
  ECONNABORTED: 'Timed out or aborted. Please try again or contact support!',
}

export function deriveErrors(error: AxiosError<{detail: string} | Record<string, string[]>>, knownFields: string[]): FormErrorSet {
  const errorSet: FormErrorSet = {
    fields: {},
    errors: [],
  }
  if (!error.response || !error.response.data || !(typeof error.response.data === 'object')) {
    if (error.code && TRANSLATED[error.code]) {
      errorSet.errors.push(TRANSLATED[error.code])
      return errorSet
    }
    console.trace(error)
    errorSet.errors = ['We had an issue contacting the server. Please try again later!']
    return errorSet
  }
  const unresolved: FormError = {}
  if (Array.isArray(error.response.data)) {
    errorSet.errors.push(...error.response.data)
    return errorSet
  }
  for (const key of Object.keys(error.response.data)) {
    if (knownFields.indexOf(key) !== -1) {
      // @ts-ignore
      errorSet.fields[key] = error.response.data[key]
    } else if (key !== 'detail') {
      // @ts-ignore
      unresolved[key] = error.response.data[key]
    }
  }
  if (error.response.data.detail && !Array.isArray(error.response.data.detail)) {
    errorSet.errors.push(error.response.data.detail)
  }
  if (Object.keys(unresolved).length) {
    errorSet.errors.push(...missingFieldError(unresolved))
  }
  return errorSet
}
