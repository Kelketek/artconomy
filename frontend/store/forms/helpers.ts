import {AxiosError} from 'axios'
import {FormError} from '@/store/forms/types/FormError'
import {FormErrorSet} from '@/store/forms/types/FormErrorSet'

export function missingFieldError(errors: FormError): string[] {
  const result: string[] = []
  for (const key of Object.keys(errors)) {
    result.push(
      'Whoops! We had a coding error. Please contact support and tell them the following: ' +
      key + ': ' + errors[key].join(' '))
  }
  return result
}

export function deriveErrors(error: AxiosError, knownFields: string[]): FormErrorSet {
  const errorSet: FormErrorSet = {
    fields: {},
    errors: [],
  }
  if (!error.response || !error.response.data || !(typeof error.response.data === 'object')) {
    console.trace(error)
    errorSet.errors = ['We had an issue contacting the server. Please try again later!']
    return errorSet
  }
  const unresolved: FormError = {}
  for (const key of Object.keys(error.response.data)) {
    if (knownFields.indexOf(key) !== -1) {
      errorSet.fields[key] = error.response.data[key]
    } else if (key !== 'detail') {
      unresolved[key] = error.response.data[key]
    }
  }
  if (error.response.data.detail) {
    errorSet.errors.push(error.response.data.detail)
  }
  if (Object.keys(unresolved).length) {
    errorSet.errors.push(...missingFieldError(unresolved))
  }
  return errorSet
}
