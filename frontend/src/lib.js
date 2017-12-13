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
  return $.ajax({
    url,
    method,
    data: data ? JSON.stringify(data) : undefined,
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    success,
    error
  })
}

export function ratings () {
  return [
    {id: 0, name: 'Clean/Safe for work'},
    {id: 1, name: 'Risque/mature, not adult content but not safe for work'},
    {id: 2, name: 'Adult content, not safe for work'}
  ]
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
