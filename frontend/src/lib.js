import moment from 'moment'
import jquery from 'jquery'
import MarkDownIt from 'markdown-it'
import Vue from 'vue'

const $ = jquery

export const md = MarkDownIt()

export function getCookie (name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i += 1) {
      const cookie = $.trim(cookies[i])
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (`${name}=`)) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export function formatDate (dateString) {
  return moment(dateString).format('MMMM Do YYYY, h:mm:ss a')
}

// https://stackoverflow.com/questions/14573223/set-cookie-and-get-cookie-with-javascript
export function setCookie (name, value, days) {
  let expires = ''
  if (days) {
    let date = new Date()
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
    expires = '; expires=' + date.toUTCString()
  }
  document.cookie = name + '=' + value + expires + '; path=/'
}

function csrfSafeMethod (method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
}

$.ajaxSetup({
  beforeSend (xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'))
      xhr.setRequestHeader('Authorization', getCookie('authtoken'))
    }
  }
})

function findField (fieldname) {
  return function wrapped (field) {
    return field.model === fieldname
  }
}

export function setErrors (form, errors) {
  const errorSet = []
  for (const fieldname of Object.keys(errors)) {
    let targetField = form.fields.find(findField(fieldname))
    if (targetField) {
      for (const error of Object.keys(errors[fieldname])) {
        errorSet.push({field: targetField, error: errors[fieldname][error]})
      }
    }
  }
  if (errorSet.length) {
    EventBus.$emit('form-failure', errorSet)
  }
  form.errors = errorSet
}

export function artCall (url, method, data, success, error) {
  if (method !== 'GET') {
    data = data ? JSON.stringify(data) : undefined
  }
  return $.ajax({
    url,
    method,
    data: data,
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    success,
    error
  })
}

export const RATINGS = {
  0: 'Clean/Safe for work',
  1: 'Risque/mature, not adult content but not safe for work',
  2: 'Adult content, not safe for work',
  3: 'Offensive/Disturbing to most viewers, not safe for work'
}

export const RATINGS_SHORT = {
  0: 'Clean/Safe',
  1: 'Risque',
  2: 'Adult content',
  3: 'Offensive/Disturbing'
}

export function genOptions (enumerable) {
  let options = []
  for (let key of Object.keys(enumerable)) {
    options.push({value: key, text: enumerable[key]})
  }
  return options
}

export function ratings () {
  return genOptions(RATINGS)
}

export function ratingsShort () {
  return genOptions(RATINGS_SHORT)
}

export const NOTIFICATION_MAPPING = {
  '2': 'ac-char-transfer',
  '3': 'ac-char-tag',
  '4': 'ac-comment-notification',
  '10': 'ac-submission-tag',
  '14': 'ac-favorite',
  '15': 'ac-dispute',
  '16': 'ac-refund',
  '17': 'ac-submission-char-tag',
  '18': 'ac-order-update',
  '19': 'ac-sale-update',
  '22': 'ac-revision-uploaded'
}

export const ORDER_STATUSES = {
  '1': 'has been placed, and needs your acceptance!',
  '2': 'requires payment to continue.',
  '3': 'has been added to your queue.',
  '4': 'is currently in progress!',
  '5': 'is waiting for your review.',
  '6': 'has been cancelled.',
  '7': 'has been placed under dispute.',
  '8': 'has been completed!',
  '9': 'has been refunded.'
}

export const ACCOUNT_TYPES = {
  '0': 'Checking',
  '1': 'Savings'
}

export const ISSUERS = {
  1: {'name': 'Visa', 'icon': 'fa-cc-visa'},
  2: {'name': 'Mastercard', 'icon': 'fa-cc-mastercard'},
  3: {'name': 'American Express', 'icon': 'fa-cc-amex'},
  4: {'name': 'Discover', 'icon': 'fa-cc-discover'},
  5: {'name': "Diner's Club", 'icon': 'fa-cc-diners-club'}
}

export function accountTypes () {
  return genOptions(ACCOUNT_TYPES)
}

export function textualize (markdown) {
  let container = document.createElement('div')
  container.innerHTML = md.render(markdown)
  return container.textContent.trim()
}

export function setMetaContent (tagname, value) {
  let desctag = document.head.querySelector(`meta[name=${tagname}]`)
  if (!desctag) {
    desctag = document.createElement('meta')
    desctag.setAttribute('name', tagname)
    document.head.appendChild(desctag)
  }
  desctag.content = value
}

export function paramHandleMap (handleName, clearList, permittedNames, defaultTab) {
  clearList = clearList || []
  return {
    get () {
      let tab = 'tab-' + this.$route.params[handleName]
      if (tab === 'tab-undefined') {
        return defaultTab
      }
      if (permittedNames !== undefined) {
        if (permittedNames.indexOf(tab) === -1) {
          return defaultTab
        }
      }
      return tab
    },
    set (value) {
      let params = {}
      params[handleName] = value.replace(/^tab-/, '')
      let newParams = Object.assign({}, this.$route.params, params)
      for (let param of clearList) {
        delete newParams[param]
      }
      let newQuery = Object.assign({}, this.$route.query)
      delete newQuery['page']
      let newPath = {name: this.$route.name, params: newParams, query: newQuery}
      this.$router.history.replace(newPath)
    }
  }
}

export function inputMatches (inputName, errorText) {
  return (value, field, model) => {
    if (value !== model[inputName]) {
      return [errorText]
    } else {
      return []
    }
  }
}

export function buildQueryString (obj) {
  let str = []
  for (let p of Object.keys(obj)) {
    if (Array.isArray(obj[p])) {
      for (let entry of obj[p]) {
        str.push(encodeURIComponent(p) + '=' + encodeURIComponent(entry))
      }
      continue
    }
    str.push(encodeURIComponent(p) + '=' + encodeURIComponent(obj[p]))
  }
  return str.join('&')
}

export function validateNonEmpty (value) {
  if (!value.length) {
    return 'This field is required!'
  }
}

// From vue upload component
export function formatSize (size) {
  if (size > 1024 * 1024 * 1024 * 1024) {
    return (size / 1024 / 1024 / 1024 / 1024).toFixed(2) + ' TB'
  } else if (size > 1024 * 1024 * 1024) {
    return (size / 1024 / 1024 / 1024).toFixed(2) + ' GB'
  } else if (size > 1024 * 1024) {
    return (size / 1024 / 1024).toFixed(2) + ' MB'
  } else if (size > 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  }
  return size.toString() + ' B'
}

// The Vue form generator number validator doesn't always seem to work right. Here's our own implementation.
export function validNumber (value, schema) {
  if (isNaN(value)) {
    return ['That is not a number']
  }
  // Might be best to use type coercion here and set min and max as a string so that it displays without extra digits.
  if (schema.max !== undefined && (Number(value) > Number(schema.max))) {
    return ['This number cannot be greater than ' + schema.max]
  }
  if (schema.min !== undefined && (Number(value) < Number(schema.min))) {
    return ['This number cannot be less than ' + schema.min]
  }
  return true
}

export function minimumOrZero (value, schema) {
  if (value === 0) {
    return true
  }
  if (value < schema.min) {
    return ['Value must be either 0 or ' + schema.min]
  }
}

export const EventBus = new Vue()

export const recaptchaSiteKey = '6LdDkkIUAAAAAFyNzBAPKEDkxwYrQ3aZdVb1NKPw'
