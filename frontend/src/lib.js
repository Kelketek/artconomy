import moment from 'moment'
import jquery from 'jquery'
import MarkDownIt from 'markdown-it'

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
  for (const fieldname in errors) {
    let targetField = form.fields.find(findField(fieldname))
    if (targetField) {
      for (const error in errors[fieldname]) {
        errorSet.push({field: targetField, error: errors[fieldname][error]})
      }
    }
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

export const PRODUCT_TYPES = {
  0: 'Sketch',
  1: 'Full Body',
  2: 'Reference Sheet',
  3: 'Convention badge/button/card',
  4: 'Single Icon',
  5: 'Icon/Sticker set',
  6: 'Headshot',
  7: 'Chibi',
  8: 'Game asset/skin',
  9: '3D Rendered Image',
  10: 'Animated (2D)',
  11: 'Animated (3D)',
  12: 'Short Story',
  13: 'Long story',
  14: 'Music',
  15: 'Other'
}

function genOptions (enumerable) {
  let contentRatings = []
  for (let key in Object.keys(enumerable)) {
    contentRatings.push({id: key, name: enumerable[key]})
  }
  return contentRatings
}

export function ratings () {
  return genOptions(RATINGS)
}

export function ratingsShort () {
  return genOptions(RATINGS_SHORT)
}

export function productTypes () {
  return genOptions(PRODUCT_TYPES)
}

export const NOTIFICATION_MAPPING = {
  '14': 'ac-favorite',
  '15': 'ac-dispute',
  '16': 'ac-refund'
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

export function paramHandleMap (handleName, tabMap, clearList) {
  const numMap = {}
  clearList = clearList || []

  for (let key of Object.keys(tabMap)) {
    numMap[tabMap[key]] = key
  }
  return {
    get () {
      let val = tabMap[this.$route.params[handleName]]
      if (val === undefined) {
        val = 0
      }
      return val
    },
    set (value) {
      let params = {}
      params[handleName] = numMap[value]
      let newParams = Object.assign({}, this.$route.params, params)
      for (let param of clearList) {
        delete newParams[param]
      }
      this.$router.history.replace({name: this.$route.name, params: newParams})
    }
  }
}

export function inputMatches (inputName, errorText) {
  return (value, field, model) => {
    if (value !== model[inputName]) {
      console.log(value)
      console.log(model[inputName])
      return [errorText]
    } else {
      return []
    }
  }
}
