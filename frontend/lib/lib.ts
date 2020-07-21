import moment from 'moment-timezone'
import axios, {AxiosRequestConfig, AxiosResponse, CancelToken} from 'axios'
import MarkDownIt from 'markdown-it'
import Vue from 'vue'
import Token from 'markdown-it/lib/token'
import {Options} from 'markdown-it/lib'
import Renderer from 'markdown-it/lib/renderer'
import Router, {RawLocation, Route} from 'vue-router'
import StateCore from 'markdown-it/lib/rules_core/state_core'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import {SingleController} from '@/store/singles/controller'
import {AnonUser} from '@/store/profiles/types/AnonUser'
import {User} from '@/store/profiles/types/User'
import FileSpec from '@/types/FileSpec'
import {SimpleQueryParams} from '@/store/helpers/SimpleQueryParams'
import {Dictionary} from 'vue-router/types/router'
import {NamelessFormSchema} from '@/store/forms/types/NamelessFormSchema'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs'
import {ListController} from '@/store/lists/controller'
import {cloneDeep} from 'lodash'

// Needed for Matomo.
declare global {
  // noinspection JSUnusedGlobalSymbols
  interface Window {
    _paq: Array<any[]>
  }
}

window._paq = window._paq || []

// Useful for attaching dummy observers to objects that Vue needs to ignore.
export const Observer = (new Vue()).$data.__ob__.constructor

export function neutralize(obj: any) {
  // Makes an object non-reactive
  obj.__ob__ = new Observer({})
  return obj
}

export const md = MarkDownIt({linkify: true, breaks: true})
neutralize(md)

type TokenRenderer = (
  tokens: Token[], idx: number, options: Options, env: any, self: Renderer,
) => string

export const defaultRender: TokenRenderer = (
  tokens: Token[], idx: number, options: Options, env: any, self: Renderer,
): string => {
  return self.renderToken(tokens, idx, options)
}

export function isForeign(url: string) {
  if (url.toLowerCase().startsWith('mailto:')) {
    return false
  }
  // noinspection RedundantIfStatementJS
  if (url.startsWith('/') ||
    url.match(/^http(s)?:[/][/](www[.])?artconomy[.]com([/]|$)/) ||
    url.match(/^http(s)?:[/][/]artconomy[.]vulpinity[.]com([/]|$)/)) {
    return false
  }
  return true
}

md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  // @ts-ignore
  if (window.PRERENDERING) {
    return tokens[idx].content
  }
  tokens[idx].attrPush(['target', '_blank']) // add new attribute
  const hrefIndex = tokens[idx].attrIndex('href')
  // Should always have href for a link.
  let href = tokens[idx].attrs[hrefIndex][1]
  if (isForeign(href)) {
    tokens[idx].attrPush(['rel', 'nofollow noopener'])
    return defaultRender(tokens, idx, options, env, self)
  }
  // Local dev URL format.
  href = href.replace(/^http(s)?:[/][/]artconomy[.]vulpinity[.]com([/]|$)/, '/')
  // Public server format.
  href = href.replace(/^http(s)?:[/][/](www[.])?artconomy[.]com([/]|$)/, '/')
  href = encodeURI(href)
  if (!href.startsWith('mailto:')) {
    tokens[idx].attrPush(['onclick', `artconomy.$router.history.push('${href}');return false`])
  }
  return defaultRender(tokens, idx, options, env, self)
}

md.renderer.rules.link_close = (tokens, idx, options, env, self) => {
  // @ts-ignore
  if (window.PRERENDERING) {
    return ''
  }
  return defaultRender(tokens, idx, options, env, self)
}

export function mention(state: StateCore, silent?: boolean) {
  let token: Token
  let pos = state.pos
  const ch = state.src.charCodeAt(pos)

  // Bug out if this @ is in the middle of a word instead of the beginning.
  const prCh = state.src[pos - 1]
  if (prCh !== undefined) {
    if (!/^\s+$/.test(prCh)) { return }
  }
  if (ch !== 0x40/* @ */) { return false }
  const start = pos
  pos++
  const max = state.posMax

  while (pos < max && /[-a-zA-Z_0-9]/.test(state.src[pos])) { pos++ }
  if (pos - start === 1) {
    // Hanging @.
    return
  }

  const marker = state.src.slice(start, pos)

  // Never found an instance where this is true, but the MarkdownIt rules require handling it.
  /* istanbul ignore else */
  if (!silent) {
    token = state.push('mention', 'ac-avatar', 0)
    token.content = marker
    state.pos = pos
    return true
  }
}

md.renderer.rules.mention = (tokens, idx) => {
  const token = tokens[idx]
  const username = token.content.slice(1, token.content.length)
  // Must have no returns, or will affect spacing.
  return '<span style="display:inline-block;vertical-align: bottom;">' +
    `<ac-avatar username="${username}"></ac-avatar></span>`
}

md.inline.ruler.push('mention', mention, ['mention'])

export function getCookie(name: string): string | null {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let cookie of cookies) {
      cookie = cookie.trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (`${name}=`)) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export function formatDateTime(dateString: string) {
  return moment(dateString).format('MMMM Do YYYY, h:mm:ss a')
}

export function formatDate(dateString: string) {
  return moment(dateString).format('MMMM Do YYYY')
}

export function formatDateTerse(dateString: string) {
  const date = moment(dateString)
  if (date.year() !== moment().year()) {
    return date.format('MMM Do YY')
  }
  return date.format('MMM Do')
}

// https://stackoverflow.com/questions/14573223/set-cookie-and-get-cookie-with-javascript
export function setCookie(name: string, value: any, days?: number) {
  let expires = ''
  if (days) {
    const date = new Date()
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
    expires = '; expires=' + date.toUTCString()
  }
  let cookieVal = name + '=' + value + expires + '; path=/'
  /* istanbul ignore if */
  if (process.env.NODE_ENV === 'production') {
    cookieVal += 'l Secure;'
  }
  document.cookie = cookieVal
}

export function deleteCookie(name: string) {
  document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
}

export function csrfSafeMethod(method: string) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method.toUpperCase()))
}

export function crossDomain(url: string) {
  const urlAnchor = document.createElement('a')
  urlAnchor.href = url
  const originAnchor = document.createElement('a')
  originAnchor.href = location.href
  return originAnchor.protocol + '//' + originAnchor.host !== urlAnchor.protocol + '//' + urlAnchor.host
}

interface Headers {
  [key: string]: string
}

export function getHeaders(method: HttpVerbs, url: string): Headers {
  const headers = {} as Headers
  headers['Content-Type'] = 'application/json; charset=utf-8'
  if (!csrfSafeMethod(method) && !crossDomain(url)) {
    const token = getCookie('csrftoken')
    const referredBy = getCookie('referredBy')
    if (token) {
      headers['X-CSRFToken'] = token
    }
    if (referredBy) {
      headers['X-Referred-By'] = referredBy
    }
  }
  return headers
}

declare interface ArtCallBaseOptions {
  url: string,
  method: HttpVerbs,
  data?: any,
  preSuccess?: (response: AxiosResponse) => void,
  cancelToken?: CancelToken
}

export type ArtCallOptions = AxiosRequestConfig & ArtCallBaseOptions

export function artCall(options: ArtCallOptions): Promise<any> {
  let preSuccess: (response: AxiosResponse) => any
  if (!options.preSuccess) {
    preSuccess = (response: AxiosResponse) => {
      return response.data
    }
  } else {
    preSuccess = options.preSuccess
  }
  const config = {...options}
  delete config.preSuccess
  config.headers = getHeaders(config.method, options.url)
  return axios.request(config).then(preSuccess)
}

export const RATINGS = {
  0: 'Clean/Safe for work',
  1: 'Risque/mature, not adult content but not safe for work',
  2: 'Adult content, not safe for work',
  3: 'Offensive/Disturbing to most viewers, not safe for work',
}

export const RATINGS_SHORT = {
  0: 'Clean/Safe',
  1: 'Risque',
  2: 'Adult content',
  3: 'Offensive/Disturbing',
}

export function genOptions(enumerable: { [key: number]: string }) {
  const options = [] as Array<{ value: string, text: string }>
  for (const key of Object.keys(enumerable)) {
    options.push({value: key, text: enumerable[parseInt(key, 10)]})
  }
  return options
}

export function ratings() {
  return genOptions(RATINGS)
}

export function ratingsNonExtreme() {
  const nonExtreme = {...RATINGS}
  delete nonExtreme[3]
  return genOptions(nonExtreme)
}

export function ratingsShort() {
  return genOptions(RATINGS_SHORT)
}

export interface TypeToValue {
  [key: number]: string,
}

export const NOTIFICATION_MAPPING: TypeToValue = {
  0: 'ac-new-character',
  3: 'ac-char-tag',
  4: 'ac-comment-notification',
  6: 'ac-new-product',
  7: 'ac-commissions-open',
  10: 'ac-submission-tag',
  14: 'ac-favorite',
  15: 'ac-dispute',
  16: 'ac-refund',
  17: 'ac-submission-char-tag',
  18: 'ac-order-update',
  19: 'ac-sale-update',
  21: 'ac-submission-artist-tag',
  22: 'ac-revision-uploaded',
  23: 'ac-submission-shared',
  24: 'ac-char-shared',
  25: 'ac-new-pm',
  26: 'ac-streaming',
  27: 'ac-renewal-failure',
  28: 'ac-subscription-deactivated',
  29: 'ac-renewal-fixed',
  30: 'ac-new-journal',
  31: 'ac-order-token-issued',
  32: 'ac-withdraw-failed',
  33: 'ac-portrait-referral',
  34: 'ac-landscape-referral',
  35: 'ac-reference-uploaded',
  36: 'ac-waitlist-updated',
}

export const ORDER_STATUSES: TypeToValue = {
  1: 'has been placed, and needs your acceptance!',
  2: 'requires payment to continue.',
  3: 'has been added to your queue.',
  4: 'is currently in progress!',
  5: 'is waiting for your review.',
  6: 'has been cancelled.',
  7: 'has been placed under dispute.',
  8: 'has been completed!',
  9: 'has been refunded.',
}

export const ACCOUNT_TYPES: TypeToValue = {
  0: 'Checking',
  1: 'Savings',
}

export const ISSUERS = {
  1: {name: 'Visa', icon: 'fa-cc-visa'},
  2: {name: 'Mastercard', icon: 'fa-cc-mastercard'},
  3: {name: 'American Express', icon: 'fa-cc-amex'},
  4: {name: 'Discover', icon: 'fa-cc-discover'},
  5: {name: 'Diner\'s Club', icon: 'fa-cc-diners-club'},
}

export function textualize(markdown: string) {
  const container = document.createElement('div')
  container.innerHTML = md.render(markdown)
  return (container.textContent && container.textContent.trim()) || ''
}

export function clearMetaTag(tagname: string) {
  const tag = document.head.querySelector(`meta[name=${tagname}]`)
  if (tag && tag.parentNode) {
    tag.parentNode.removeChild(tag)
  }
}

export function setMetaContent(tagname: string, value: string, attributes?: {[key: string]: string}) {
  let desctag = document.head.querySelector(`meta[name=${tagname}]`)
  if (desctag) {
    desctag.remove()
  }
  desctag = document.createElement('meta')
  desctag.setAttribute('name', tagname)
  desctag.textContent = value
  if (attributes) {
    for (const key of Object.keys(attributes)) {
      desctag.setAttribute(key, attributes[key])
    }
  }
  document.head.appendChild(desctag)
}

export function singleQ(value: string | Array<string | null>): string {
  if (Array.isArray(value)) {
    return value[0] || ''
  }
  return value || ''
}

declare type paramDecorator = (cls: Vue, propName: string) => void

export function paramHandleMap(
  handleName: string, clearList?: string[], permittedNames?: string[], defaultTab?: string,
): paramDecorator {
  return (cls, propName) => {
    Object.defineProperty(cls, propName, {
      get(): string {
        const tab = 'tab-' + (this as Vue).$route.params[handleName]
        if (tab === 'tab-undefined') {
          return defaultTab || ''
        }
        if (permittedNames !== undefined) {
          if (permittedNames.indexOf(tab) === -1) {
            return defaultTab || ''
          }
        }
        return tab
      },
      set(value: string) {
        const params: { [key: string]: string } = {}
        params[handleName] = value.replace(/^tab-/, '')
        const newParams = Object.assign({}, (this as Vue).$route.params, params)
        for (const param of clearList || []) {
          delete newParams[param]
        }
        const newQuery = Object.assign({}, (this as Vue).$route.query)
        delete newQuery.page
        const newPath = {name: (this as Vue).$route.name, params: newParams, query: newQuery};
        (this as Vue).$router.replace(newPath as RawLocation)
      },
    })
  }
}

export function paramHandleArray(handleName: string, nameArray: string[]): paramDecorator {
  function updatePath(component: Vue, value: number) {
    const params: {[key: string]: any} = {}
    params[handleName] = nameArray[value]
    const newParams = Object.assign({}, component.$route.params, params)
    const newQuery = Object.assign({}, component.$route.query)
    delete newQuery.page
    /* istanbul ignore next */
    const name = component.$route.name || undefined
    const newPath = {name, params: newParams, query: newQuery}
    component.$router.replace(newPath)
  }
  return (cls, propName) => {
    Object.defineProperty(cls, propName, {
      get() {
        if (this.$route.params[handleName] === undefined) {
          updatePath(this, 0)
          return 0
        }
        return nameArray.indexOf(this.$route.params[handleName])
      },
      set(value: number) {
        updatePath(this, value)
      },
    })
  }
}

export function formatSize(size: number): string {
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

export function truncateText(text: string, maxLength: number) {
  if (text.length <= maxLength) {
    return text
  }
  const newText = text.slice(0, maxLength)
  let iterator = 0
  // Find the first space break before that point.
  while (iterator < newText.length) {
    const testText = newText.slice(0, newText.length - iterator)
    if (([' ', '\n', '\r', '\t'].indexOf(testText[testText.length - 1]) === -1)) {
      iterator += 1
      continue
    }
    return testText.trimEnd() + '...'
  }
  // Super long word for some reason.
  return newText + '...'
}

const ICON_EXTENSIONS = [
  'ACC', 'AE', 'AI', 'AN', 'AVI', 'BMP', 'CSV', 'DAT', 'DGN', 'DOC', 'DOCH', 'DOCM', 'DOCX', 'DOTH', 'DW', 'DWFX',
  'DWG', 'DXF', 'DXL', 'EML', 'EPS', 'F4A', 'F4V', 'FLV', 'FS', 'GIF', 'HTML', 'IND', 'JPEG', 'JPG',
  'JPP', 'LR', 'LOG',
  'M4V', 'MBOX', 'MDB', 'MIDI', 'MKV', 'MOV', 'MP3', 'MP4', 'MPEG', 'MPG', 'MPP', 'MPT', 'MPW', 'MPX', 'MSG', 'ODS',
  'OGA', 'OGG', 'OGV', 'ONE', 'OST', 'PDF', 'PHP', 'PNG', 'POT', 'POTH', 'POTM', 'POTX', 'PPS', 'PPSX',
  'PPT', 'PPTH',
  'PPTM', 'PPTX', 'PREM', 'PS', 'PSD', 'PST', 'PUB', 'PUBH', 'PUBM', 'PWZ', 'READ', 'RP', 'RTF', 'SQL', 'SVG', 'SWF',
  'TIF', 'TIFF', 'TXT', 'URL', 'VCF', 'VDX', 'VOB', 'VSD', 'VSS', 'VST', 'VSX', 'VTX', 'WAV', 'WDP', 'WEBM', 'WMA',
  'WMV', 'XD', 'XLS', 'XLSM', 'XLSX', 'XML', 'ZIP',
]

export const COMPONENT_EXTENSIONS = {
  MP4: 'ac-video-player',
  WEBM: 'ac-video-player',
  OGV: 'ac-video-player',
  TXT: 'ac-markdown-viewer',
  MP3: 'ac-audio-player',
  WAV: 'ac-audio-player',
  OGG: 'ac-audio-player',
}

export function getExt(filename: string): string {
  filename = filename || ''
  const components = filename.split('.')
  return components[components.length - 1].toUpperCase() as string
}

//
export function isImage(filename: string) {
  return !(['JPG', 'BMP', 'JPEG', 'GIF', 'PNG', 'SVG'].indexOf(getExt(filename)) === -1)
}

//
export function extPreview(filename: string) {
  let ext: string| 'UN.KNOWN' = getExt(filename)
  if (ICON_EXTENSIONS.indexOf(ext) === -1) {
    ext = 'UN.KNOWN'
  }
  return `/static/icons/${ext}.png`
}

export function isAxiosError(err: any) {
  // Determines if a thrown error is an error from Axios-- in which case it's a network/API issue, or else some other
  // kind, indicating a bug.
  return Boolean(err.response || err.request)
}

export function genId() {
  let text = ''
  const possible = 'abcdefghijklmnopqrstuvwxyz'
  for (let i = 0; i < 20; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length))
  }
  return text
}

export const RECAPTCHA_SITE_KEY = '6LdDkkIUAAAAAFyNzBAPKEDkxwYrQ3aZdVb1NKPw'

export const RATING_LONG_DESC = {
  0: `Content which can be safely viewed in most workplaces. Pieces with nudity
                    or especially suggestive clothing do not belong in this category. Pieces with violence or
                    offensive messages do not belong in this category, either.`,
  1: `This is for content which may contain nudity or risque content (such as fetish clothing and/or gear) which
         is not suitable for work but is not explicitly pornographic belongs here.
                    Mild violence also belongs in this category.`,
  2: `This is for content which is explicitly pornographic but unlikely to violate the
                    sensibilities of most viewers of such content. Moderate violence also belongs in this category.`,
  3: `This is for content which is extreme in some regard, such as fetish artwork
                    that most viewers would find 'squicky' or disturbing or portrayals of extreme violence.`,
}

export const RATING_COLOR = {
  0: 'green',
  1: 'blue',
  2: 'red',
  3: 'black',
}

export function dotTraverse(start: any, dotPath: string, silent?: boolean) {
  const path = dotPath.split('.')
  let value: any = start
  const currentRoute: string[] = []
  for (const namespace of path) {
    if (value === undefined) {
      if (silent) {
        return undefined
      }
      throw Error(`Property ${currentRoute.join('.')} is not defined.`)
    }
    currentRoute.push(namespace)
    value = value[namespace]
  }
  return value
}

export function flatten(name: string) {
  return name.replace(/[./]/g, '_')
}

export function posse(userList: string[], additional: number) {
  userList = userList.map((username) => deriveDisplayName(username))
  if (userList.length === 2 && !additional) {
    return `${userList[0]} and ${userList[1]}`
  }
  if (userList.length === 3 && !additional) {
    return `${userList[0]}, ${userList[1]}, and ${userList[2]}`
  }
  let group = userList.join(', ')
  if (additional) {
    group += ' and ' + additional
    if (additional === 1) {
      group += ' other'
    } else {
      group += ' others'
    }
  }
  return group
}

export function immediate(val: any) {
  return new Promise((resolve) => {
    resolve(val)
  })
}

// We have the upload form in several places, and they may load in different orders, so it's best to have the schema
// broken out for quick initialization if need be. This function might be better placed elsewhere.
export function newUploadSchema(userHandler: SingleController<TerseUser|User|AnonUser>) {
  return {
    endpoint: `${userHandler.endpoint}submissions/`,
    fields: {
      title: {value: '', step: 2},
      caption: {value: '', step: 2},
      private: {value: false, step: 2},
      comments_disabled: {value: false, step: 2},
      rating: {value: 0, step: 1},
      file: {value: '', step: 1},
      preview: {value: '', step: 1},
      tags: {value: [], step: 1},
      characters: {value: [], step: 1},
      artists: {value: [], step: 1},
    },
  }
}

export function searchSchema() {
  return {
    // Endpoint will be ignored here.
    endpoint: '/',
    fields: {
      q: {value: '', omitIf: ''},
      watch_list: {value: null, omitIf: null},
      shield_only: {value: null, omitIf: null},
      featured: {value: null, omitIf: null},
      rating: {value: null, omitIf: null},
      lgbt: {value: null, omitIf: null},
      artists_of_color: {value: null, omitIf: null},
      max_price: {value: '', omitIf: ''},
      min_price: {value: '', omitIf: ''},
    },
  }
}

export function thumbFromSpec(thumbName: string, spec: FileSpec) {
  if ((['gallery', 'full', 'preview'].indexOf(thumbName) !== -1) && getExt(spec.full) === 'GIF') {
    return spec.full
  }
  if (spec[thumbName]) {
    return spec[thumbName]
  }
  return spec.full
}

export function makeQueryParams(obj: object) {
  const result: SimpleQueryParams = {}
  for (const key of Object.keys(obj)) {
    result[key] = (obj as any)[key] + ''
  }
  return result
}

export function fallback(query: Dictionary<string | Array<string | null>>, field: string, defaultValue: any) {
  if (field in query) {
    return query[field]
  } else {
    return defaultValue
  }
}

export function fallbackBoolean(query: Dictionary<string | Array<string | null>>, field: string, defaultValue: any) {
  const prelim = fallback(query, field, defaultValue)
  if (prelim === null) {
    return null
  }
  return JSON.parse(prelim)
}

export function baseCardSchema(endpoint: string): NamelessFormSchema {
  return {
    method: 'post',
    endpoint,
    fields: {
      first_name: {value: '', validators: [{name: 'required'}]},
      last_name: {value: '', validators: [{name: 'required'}]},
      zip: {value: '', validators: [{name: 'required'}]},
      number: {value: '', validators: [{name: 'creditCard'}, {name: 'required'}]},
      exp_date: {value: '', validators: [{name: 'cardExp'}, {name: 'required'}]},
      cvv: {value: '', validators: [{name: 'cvv', args: ['number']}, {name: 'required'}]},
      country: {value: 'US'},
      make_primary: {value: true},
      save_card: {value: true},
      card_id: {value: null},
    },
  }
}

export function baseInvoiceSchema(endpoint: string): NamelessFormSchema {
  return {
    method: 'post',
    endpoint,
    fields: {
      price: {value: 25},
      completed: {value: false},
      task_weight: {value: 0},
      revisions: {value: 1},
      private: {value: false},
      product: {value: null},
      rating: {value: 0},
      details: {value: ''},
      paid: {value: false},
      hold: {value: false},
      buyer: {value: ''},
      expected_turnaround: {value: 1},
    },
  }
}

export function deriveDisplayName(username: string) {
  if (!username) {
    return ''
  }
  if (username === '_') {
    return ''
  }
  if (username.startsWith('__deleted')) {
    return '[deleted]'
  }
  if (username.startsWith('__')) {
    // @ts-ignore
    return `Guest #${username.match(/__([0-9]+)/)[1]}`
  }
  return username
}

export function guestName(username: string) {
  if (username.indexOf(' #') !== -1) {
    return true
  }
  return (username.startsWith('__'))
}

declare interface Helper {
  mask: string,
  cvv: string,
}

export const cardHelperMap: { [key: string]: Helper } = {
  amex: {mask: '#### ###### #####', cvv: '4 digit number on front of card'},
  default: {mask: '#### #### #### ####', cvv: '3 digit number on back of card'},
}

export function saneNav(originalFunction: (location: RawLocation) => Promise<Route>) {
  // @ts-ignore
  function wrapped(this: Router, location) {
    originalFunction.call(this, location).catch((err: Error) => {
      /* istanbul ignore else */
      // @ts-ignore
      if (err && err.name === 'NavigationDuplicated') {
        // This never matters.
        return
      }
      /* istanbul ignore next */
      throw err
    })
  }

  wrapped.PATCHED = true
  return wrapped
}

export function paramsKey(sourceParams: {[key: string]: string}) {
  let key = ''
  const params = Object.keys(sourceParams)
  params.sort()
  for (const param of params) {
    if (param.endsWith('Id') || param.endsWith('Name') || param === 'username') {
      key += `${param}:${sourceParams[param]}|`
    }
  }
  return key
}

export function updateTitle(title: string) {
  document.title = title
  window._paq.push(['setDocumentTitle', document.title])
}

export function profileLink(user: User|TerseUser|null) {
  if (!user) {
    return null
  }
  if (guestName(user.username)) {
    return null
  }
  if (user.artist_mode) {
    return {name: 'Products', params: {username: user.username}}
  } else {
    return {name: 'AboutUser', params: {username: user.username}}
  }
}

export function shuffle(array: any[]) {
  let currentIndex = array.length
  let temporaryValue: any
  let randomIndex: number

  // While there remain elements to shuffle...
  while (currentIndex !== 0) {
    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex)
    currentIndex -= 1

    // And swap it with the current element.
    temporaryValue = array[currentIndex]
    array[currentIndex] = array[randomIndex]
    array[randomIndex] = temporaryValue
  }

  return array
}

export async function markRead(controller: SingleController<{id: number|string, read: boolean}>, contentType: string) {
  if (!controller.x) {
    return
  }
  if (controller.x.read) {
    return
  }
  return artCall({
    url: `/api/lib/v1/read-marker/${contentType}/${controller.x.id}/`,
    method: 'post',
  }).then(() => {
    controller.updateX({read: true})
  })
}

declare type LinkUpdateOptions = {
  list: ListController<any>,
  key: string,
  subKey?: string,
  newValue: any
}

export function updateLinked(options: LinkUpdateOptions) {
  options = {...options}
  if (!options.subKey) {
    options.subKey = 'id'
  }
  if (!options.newValue) {
    return
  }
  let updateItems = options.list.list.map(x => cloneDeep(x.x))
  updateItems = updateItems.filter(
    (x) => x[options.key][options.subKey as string] === options.newValue[options.subKey as string])
  updateItems.map((x) => { x[options.key] = options.newValue })
  updateItems.map(options.list.replace)
}
