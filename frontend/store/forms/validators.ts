import {formRegistry} from './registry'
import {FieldController} from './field-controller'
import {CancelToken} from 'axios'
import deepEqual from 'fast-deep-equal'
import {artCall} from '@/lib'
import {ArtistProfile} from '@/store/profiles/types/ArtistProfile'
import {RawData} from '@/store/forms/types/RawData'

export function required(field: FieldController): string[] {
  if (!field.value) {
    return ['This field may not be blank.']
  }
  return []
}

export function email(field: FieldController): string[] {
  if (field.value.trim() === '') {
    // Should be handled by the required validator instead.
    return []
  }
  const parts = field.value.split('@')
  if (parts.length !== 2) {
    return ['Emails must contain an @ in the middle.']
  }
  const front = parts[0].trimLeft()
  const back = parts[1].trimRight()
  if (front.length === 0) {
    return ['You must include the username in front of the @.']
  }
  if (back.length === 0) {
    return ['You must include the domain name after the @.']
  }
  if (front.search(/\s/g) !== -1) {
    return ['Emails cannot have a space in the section before the @.']
  }
  if (back.search(/\s/g) !== -1) {
    return ['Emails cannot have a space in the section after the @.']
  }
  if (back.indexOf('.') === -1) {
    return ['Emails without a full domain are not supported. (Did you forget the .com?)']
  }
  return []
}

export type CardType = 'mastercard' | 'amex' | 'discover' | 'visa' | 'diners' | 'unknown'

export function cardType(value: string): CardType {
  if (/^5[1-5]/.test(value)) {
    return 'mastercard'
  }
  if (/^4/.test(value)) {
    return 'visa'
  }
  if (/^3[47]/.test(value)) {
    return 'amex'
  }
  if (/^6011/.test(value)) {
    return 'discover'
  }
  if (/^(30[0-5]|(36|38))/.test(value)) {
    return 'diners'
  }
  return 'unknown'
}

export function cvv(field: FieldController, numberField: string) {
  const cardValue = field.form.fields[numberField].value
  let len = 3
  if (!/^\d+$/.test(field.value)) {
    return ['Digits only, please']
  }
  if (cardType(cardValue.replace(/[^0-9]+/g, '')) === 'amex') {
    len = 4
  }
  if (field.value.length !== len) {
    return [`Must be ${len} digits long`]
  }
  return []
}

export function creditCard(field: FieldController) {
  if (validateCard(field.value)) {
    return []
  } else {
    return ['That is not a valid card number. Please check the card.']
  }
}

// Yoinked from Vue Form Generator
export function validateCard(input: string) {
  /*  From validator.js code
    https://github.com/chriso/validator.js/blob/master/src/lib/isCreditCard.js
  */
  const cardRegEx = new RegExp(
    '^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|' +
    '[68][0-9])[0-9]{11}|(?:2131|1800|35\\d{3})\\d{11})$',
  )
  const sanitized = input.replace(/[^0-9]+/g, '')
  if (!cardRegEx.test(sanitized)) {
    return false
  }
  let sum = 0
  let digit
  let tmpNum
  let shouldDouble
  for (let i = sanitized.length - 1; i >= 0; i--) {
    digit = sanitized.substring(i, i + 1)
    tmpNum = parseInt(digit, 10)
    if (shouldDouble) {
      tmpNum *= 2
      if (tmpNum >= 10) {
        sum += tmpNum % 10 + 1
      } else {
        sum += tmpNum
      }
    } else {
      sum += tmpNum
    }
    shouldDouble = !shouldDouble
  }

  return sum % 10 === 0 ? sanitized : false
}

export function cardExp(field: FieldController) {
  if (!field.value) {
    // Handled by required validator.
    return []
  }
  if (!/^(\d)+$/.test(field.value)) {
    return ['Numbers only, please.']
  }
  if (!/^(\d){4}$/.test(field.value)) {
    return ['Please enter full expiration date.']
  }
  const now = new Date()
  const currentYear = now.getFullYear()
  const yearFloor = currentYear - (currentYear % 100)
  const currentMonth = now.getMonth()
  const year = parseInt(field.value.slice(2), 10) + yearFloor
  // Months are zero indexed.
  const month = parseInt(field.value.slice(0, 2), 10) - 1
  if ((month > 11) || (month < 0)) {
    return ['That is not a valid month.']
  }
  if (new Date(year, month) < new Date(currentYear, currentMonth)) {
    return ['This card has expired.']
  }
  return []
}

export function matches(field: FieldController, fieldName: string, error: string) {
  if (!deepEqual(field.value, field.form.fields[fieldName].value)) {
    return [error || 'Values do not match.']
  }
  return []
}

export function validateStatus(status: number) {
  if (status >= 200 && status < 300) {
    return true
  }
  return status === 400
}

export function simpleAsyncValidator(url: string) {
  return async(field: FieldController, cancelToken: CancelToken, sendAs?: string): Promise<string[]> => {
    const data: RawData = {}
    sendAs = sendAs || field.fieldName
    data[sendAs] = field.value
    return artCall({url, method: 'post', data, cancelToken, validateStatus}
    ).then((responseData: any) => {
      return responseData[sendAs as string] || []
    })
  }
}

export async function artistRating(
  field: FieldController, cancelToken: CancelToken, targetUsername: string
): Promise<string[]> {
  const profile = field.$getProfile(targetUsername, {})
  return profile.artistProfile.get().then(() => {
    const artistProfile = profile.artistProfile.x as ArtistProfile
    if (field.value <= artistProfile.max_rating) {
      return []
    }
    return [
      'The artist has not indicated that they wish to work with content at this rating level. ' +
      'Your request is likely to be denied.',
    ]
  })
}

export function numeric(field: FieldController) {
  let value = field.value + ''
  value = value.trim()
  if (/^[-]?[0-9]*[.]?[0-9]*$/.test(value)) {
    return []
  }
  return ['Numbers only, please.']
}

export function minLength(field: FieldController, min: number) {
  const value = field.value.trim()
  if (value.length < min) {
    return [`Too short. Minimum length: ${min}.`]
  }
  return []
}

export function maxLength(field: FieldController, max: number) {
  const value = field.value.trim()
  if (value.length > max) {
    return [`Too long. Maximum length: ${max}.`]
  }
  return []
}

export function colorRef(field: FieldController) {
  const ref = field.value.trim()
  if (/^[#][0-9a-fA-F]{6}$/.test(ref)) {
    return []
  }
  return ['The color must be in the form of an RGB reference, like #000000 #FFFFFF or #c4c4c4.']
}

export const emailAsync = simpleAsyncValidator('/api/profiles/v1/form-validators/email/')
export const username = simpleAsyncValidator('/api/profiles/v1/form-validators/username/')
export const password = simpleAsyncValidator('/api/profiles/v1/form-validators/password/')

export function registerValidators() {
  formRegistry.validators.required = required
  formRegistry.validators.email = email
  formRegistry.validators.matches = matches
  formRegistry.validators.creditCard = creditCard
  formRegistry.validators.cardExp = cardExp
  formRegistry.validators.cvv = cvv
  formRegistry.validators.colorRef = colorRef
  formRegistry.validators.numeric = numeric
  formRegistry.validators.minLength = minLength
  formRegistry.validators.maxLength = maxLength
  formRegistry.asyncValidators.username = username
  formRegistry.asyncValidators.email = emailAsync
  formRegistry.asyncValidators.password = password
  formRegistry.asyncValidators.artistRating = artistRating
}
