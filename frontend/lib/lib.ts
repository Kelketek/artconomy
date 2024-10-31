import {computed, ref, Ref, watch, WatchSource} from 'vue'
import type {AxiosRequestConfig, AxiosResponse} from 'axios'
import axios from 'axios'
import {LocationQueryRaw, LocationQueryValue, RouteParamsRaw} from 'vue-router'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
import {User} from '@/store/profiles/types/User.ts'
import {SimpleQueryParams} from '@/store/helpers/SimpleQueryParams.ts'
import {NamelessFormSchema} from '@/store/forms/types/NamelessFormSchema.ts'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs.ts'
import {ListController} from '@/store/lists/controller.ts'
import {LogLevels, LogLevelsValue} from '@/types/LogLevels.ts'
import {RatingsValue} from '@/types/Ratings.ts'
import {InvoiceTypeValue} from '@/types/InvoiceType.ts'
import {FieldController} from '@/store/forms/field-controller.ts'
import {Character} from '@/store/characters/types/Character.ts'
import {Store} from 'vuex'
import {
  artistProfileEndpointFor,
  artistProfilePathFor,
  endpointFor,
  pathFor, staffPowersEndpointFor, staffPowersPathFor,
  userPathFor,
} from '@/store/profiles/helpers.ts'
import {ProfileModule} from '@/store/profiles'
import {SingleModule} from '@/store/singles'
import {ArtStore} from '@/store'
import {StaffPowers} from '@/store/profiles/types/StaffPowers.ts'
import {ArtistProfile} from '@/store/profiles/types/ArtistProfile.ts'

// Needed for Matomo.
declare global {
  // noinspection JSUnusedGlobalSymbols
  interface Window {
    _paq: Array<any[]>,
    __LOG_LEVEL__: LogLevelsValue,
  }
}

window._paq = window._paq || []
/* istanbul ignore else */
if (window.__LOG_LEVEL__ === undefined) {
  window.__LOG_LEVEL__ = LogLevels.INFO
}

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

// https://stackoverflow.com/questions/14573223/set-cookie-and-get-cookie-with-javascript
export function setCookie(name: string, value: any) {
  let expires = ''
  const date = new Date()
  date.setFullYear(date.getFullYear() + 1)
  expires = '; expires=' + date.toUTCString()
  let cookieVal = name + '=' + value + expires + '; path=/'
  /* istanbul ignore if */
  if (process.env.NODE_ENV === 'production') {
    cookieVal += ';secure'
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
  let urlAnchor: HTMLAnchorElement
  try {
    urlAnchor = document.createElement('a')
  } catch {
    // Will only happen in a test environment.
    return true
  }
  urlAnchor.href = url
  const originAnchor = document.createElement('a')
  originAnchor.href = location.href
  return (originAnchor.protocol + '//' + originAnchor.host) !== (urlAnchor.protocol + '//' + urlAnchor.host)
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
    if (window.windowId) {
      headers['X-Window-ID'] = window.windowId
    }
  }
  return headers
}

declare interface ArtCallBaseOptions {
  url: string,
  method: HttpVerbs,
  data?: any,
  preSuccess?: (response: AxiosResponse) => void,
  signal?: AbortSignal,
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

export const RATINGS: Record<RatingsValue, string> = {
  0: 'Clean/Safe for work',
  1: 'Risque/mature, not adult content but not safe for work',
  2: 'Adult content, not safe for work',
  3: 'Offensive/Disturbing to most viewers, not safe for work',
}

export const RATINGS_SHORT: Record<RatingsValue, string> = {
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
  // @ts-ignore
  delete nonExtreme[3]
  return genOptions(nonExtreme)
}

export function ratingsShortLister() {
  return genOptions(RATINGS_SHORT)
}

export const INVOICE_TYPES: Record<InvoiceTypeValue, string> = {
  0: 'Sale',
  1: 'Subscription',
  2: 'Term',
  3: 'Tip',
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

export function singleQ(value: LocationQueryValue | LocationQueryValue[]): string {
  if (Array.isArray(value)) {
    return value[0] || ''
  }
  return value || ''
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

export const RATING_LONG_DESC: Record<RatingsValue, string> = {
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

export const RATING_COLOR: Record<RatingsValue, string> = {
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
  // Note: This also makes any underscore a double underscore. This is so if we have something like two userames,
  // 'test.person' and 'test_person', it won't have the same output. It does mean that it will grow every time you
  // apply it to an already transformed string, however.
  return name.replace(/[_]/g, '__').replace(/[./]/g, '_')
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
    reset: false,
  }
}

export function searchSchema() {
  return {
    // Endpoint will be ignored here.
    endpoint: '/',
    fields: {
      q: {value: '', omitIf: ''},
      watch_list: {value: false, omitIf: false},
      shield_only: {value: false, omitIf: false},
      featured: {value: false, omitIf: false},
      rating: {value: false, omitIf: false},
      lgbt: {value: false, omitIf: false},
      commissions: {value: false, omitIf: false},
      artists_of_color: {value: false, omitIf: false},
      content_ratings: {value: '', omitIf: ''},
      minimum_content_rating: {value: 0 as RatingsValue, omitIf: 0},
      max_price: {value: '', omitIf: ''},
      min_price: {value: '', omitIf: ''},
      max_turnaround: {value: '', omitIf: ''},
      page: {value: 1},
      size: {value: 24},
    },
  }
}

export function makeQueryParams(obj: object) {
  const result: SimpleQueryParams = {}
  for (const key of Object.keys(obj)) {
    result[key] = (obj as any)[key] + ''
  }
  return result
}

export function fallback(query: LocationQueryRaw, field: string, defaultValue: any) {
  if (field in query) {
    return query[field]
  } else {
    return defaultValue
  }
}

export function fallbackBoolean(query: LocationQueryRaw, field: string, defaultValue: any) {
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
      make_primary: {value: true},
      save_card: {value: true},
      card_id: {value: null},
      use_reader: {value: false},
    },
  }
}

export function baseInvoiceSchema(endpoint: string): NamelessFormSchema {
  return {
    method: 'post',
    endpoint,
    fields: {
      price: {value: "25.00"},
      completed: {value: false},
      task_weight: {value: 0},
      revisions: {value: 1},
      private: {value: false},
      product: {value: null},
      rating: {value: 0},
      details: {value: ''},
      paid: {value: false},
      hold: {value: false},
      buyer: {value: null},
      cascade_fees: {value: false},
      expected_turnaround: {value: 1},
    },
  }
}

export function paramsKey(sourceParams: RouteParamsRaw) {
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

declare interface ReadMarkable {
  id: number|string,
  read: boolean,
}

export async function markRead<T extends ReadMarkable>(controller: SingleController<T>, contentType: string) {
  if (!controller.x) {
    return
  }
  if (controller.x.read) {
    return
  }
  return artCall({
    url: `/api/lib/read-marker/${contentType}/${controller.x.id}/`,
    method: 'post',
  }).then(() => {
    controller.updateX({read: true} as Partial<T>)
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
  let updateItems = options.list.list.map(x => clone(x.x))
  updateItems = updateItems.filter(
    (x) => x[options.key][options.subKey as string] === options.newValue[options.subKey as string])
  updateItems.map((x) => { x[options.key] = options.newValue }) // eslint-disable-line array-callback-return
  updateItems.map(options.list.replace)
}

window.__LOG_LEVEL__ = LogLevels.INFO

export const log = {
  // Eventually I want to filter log statements based on their label.
  filter: [],
  debug(...args: any[]) {
    if (window.__LOG_LEVEL__ <= LogLevels.DEBUG) {
      console.debug(...args)
    }
  },
  info(...args: any[]) {
    if (window.__LOG_LEVEL__ <= LogLevels.INFO) {
      console.info(...args)
    }
  },
  warn(...args: any[]) {
    if (window.__LOG_LEVEL__ <= LogLevels.WARN) {
      console.warn(...args)
    }
  },
  error(...args: any[]) {
    if (window.__LOG_LEVEL__ <= LogLevels.ERROR) {
      console.error(...args)
    }
  },
}

export const initDrawerValue = () => {
  // localStorage will be null on mobile, but that will always start closed anyway.
  const startValue = localStorage && localStorage.getItem('drawerOpen')
  if (startValue !== null) {
    try {
      return JSON.parse(startValue) as boolean
    } catch (err) {
      console.log(err)
      console.log('Returning null as initial drawer state.')
    }
  }
  return null
}

export const paypalTokenToUrl = (invoiceToken: string, sender: boolean): string => {
  if (!invoiceToken) {
    return ''
  }
  let extension: string
  let baseUrl: string
  if (sender) {
    extension = `/invoice/details/${invoiceToken}`
  } else {
    const tokenSegments = invoiceToken.split('INV2-', 2)
    const token = tokenSegments[tokenSegments.length - 1].replace(/-/g, '')
    extension = `/invoice/p/#${token}`
  }
  if (window.SANDBOX_APIS) {
    baseUrl = 'https://www.sandbox.paypal.com'
  } else {
    baseUrl = 'https://www.paypal.com'
  }
  return `${baseUrl}${extension}`
}

/**
 * Class decorator which makes all getters/setters computed properties for use by Vue 3's reactivity system.
 * The target class must have a Map defined on it named __getterMap.
 *
 * Note that this has some subtle implications for the getter functions, which can't be arrow functions.
 * If you need to access any refs within the getter functions, you will need to use `toRaw` to normalize them
 * as reference objects. Otherwise, Vue's internal proxying will sometimes give you raw values and other times
 * give you the reference objects depending on how the function is called.
 *
 * This getup is needed because there are so many parts of the code that expect 'raw access' to these values Vue 2
 * style that changing the controllers to use .value for all their computed properties would be a massive, error-prone
 * undertaking, and it would be more verbose than I'd like anyway.
*/
export function ComputedGetters<T extends Function> (
  Wrapped: T,
): T {
  // prototype props.
  const proto = Wrapped.prototype
  Object.getOwnPropertyNames(proto).forEach(function (key) {
    if (key === 'constructor') {
      return
    }
    const descriptor = Object.getOwnPropertyDescriptor(proto, key)!
    if (descriptor.get || descriptor.set) {
      Object.defineProperty(proto, key, {
        get() {
          if (!this.__getterMap.get(key)) {
            this.scope.run(() => {
              this.__getterMap.set(key, computed(descriptor.get!.bind(this)))
            })
          }
          return this.__getterMap.get(key).value
        },
        set(value) {
          descriptor.set!.apply(this, [value])
        }
      })
    }
  })
  return Wrapped
}

export const getSalesStatsSchema = (username: string) => ({
  endpoint: `/api/sales/account/${username}/sales/stats/`,
  socketSettings: {
    appLabel: 'profiles',
    modelName: 'ArtistProfile',
    serializer: 'SalesStatsSerializer',
  }
})

export const prepopulateCharacters = (field: FieldController, showRef: Ref<boolean>, initRef: Ref<Character[]>) => {
  if (field.value.length === 0) {
    showRef.value = true
  } else {
    const promises = []
    for (const charId of field.model) {
      promises.push(artCall({
        url: `/api/profiles/data/character/id/${charId}/`,
        method: 'get',
      }).then(
        (response) => initRef.value.push(response),
      ).catch(() => {
        field.model = field.model.filter((val: number) => val !== charId)
      }))
    }
    Promise.all(promises).then(() => {
      showRef.value = true
    })
  }
}

export const BASE_URL = window.location.origin

export const transformComponentName = (componentName: string) => {
  return componentName.split('-').map((segment) => (
    `${segment.charAt(0).toUpperCase()}${segment.substring(1)}`),
  ).join('')
}

export const setViewer = ({ store, user, artistProfile, powers }: { store: Store<any>; user: User | AnonUser | TerseUser, artistProfile?: ArtistProfile, powers?: StaffPowers }) => {
  const username = user.username
  store.registerModule(pathFor(username), new ProfileModule({viewer: true, persistent: true}))
  store.registerModule(
    userPathFor(username),
    new SingleModule<User | AnonUser | TerseUser>({
      x: user,
      ready: true,
      endpoint: endpointFor(username),
      socketSettings: {serializer: 'UserSerializer', appLabel: 'profiles', modelName: 'User'},
    }),
  )
  store.registerModule(
    artistProfilePathFor(username),
    new SingleModule<ArtistProfile>({
      x: artistProfile || null,
      ready: !!artistProfile,
      endpoint: artistProfileEndpointFor(username),
    }),
  )
  store.registerModule(
    staffPowersPathFor(username),
    new SingleModule<StaffPowers>({
      x: powers || null,
      ready: !!powers,
      endpoint: staffPowersEndpointFor(username),
    }),
  )
  store.commit('profiles/setViewerUsername', username)
  store.commit(`userModules/${username}/user/setReady`, true)
}

export const useLazyInitializer = <T>(initializer: WatchSource<T>) => {
  const reactive = ref(false)
  watch(initializer, (val) => {
    if (val) {
      reactive.value = true
    }
  })
  return reactive
}

export const loadErrorHandler = (store: ArtStore) => (event: PromiseRejectionEvent) => {
  if (!event.reason || !(event.reason instanceof Error)) {
    // Let the event fall through to propogation. No idea what's wrong here.
    return
  }
  const reason = event.reason as Error
  if (reason.name === 'TypeError') {
    const message = reason.message + ''
    if (message.startsWith('Importing a module script failed.') || message.startsWith('Failed to fetch dynamically imported module') || message.startsWith('error loading dynamically imported module')) {
      store.commit('pushAlert', {message: 'We had an issue loading part of the page. Try clicking around a bit or refreshing.', category: 'error'})
      event.preventDefault()
      event.stopPropagation()
      event.stopImmediatePropagation()
      return false
    }
  }
}

export const useForceRecompute = () => {
  // Creates a watchable ref that can be used to force recomputation in cases where it needs to be manually triggered.
  const checkTarget = ref(0)
  const recalculate = () => {
    checkTarget.value = checkTarget.value ? 0 : 1
  }
  const check = () => {checkTarget.value}
  return {check, recalculate}
}

export const starRound = (val: number|null) => {
  // Given a user's 'stars' rating, round the number of displayed stars
  // to the most intuitive value. If we didn't do this, then 4.9 would
  // render as 4.5, and 4.1 would render as 4.5.
  // We round instead the conceptually closest star.
  if (val === null) {
    return undefined
  }
  const base = Math.floor(val)
  const remainder = val % 1
  if (remainder >= .75) {
    return base + 1
  } else if (remainder <= .25) {
    return base
  }
  return base + .5
}

const PRIMITIVES = new Set(['number', 'string', 'function', 'symbol', 'bigint', 'boolean', 'undefined'])

export const clone = <T>(item: T, knownMap?: Map<any, any>): T => {
  // This is our clone function. It should handle everything we need to clone for. We used to use lodash's cloneDeep,
  // which is extremely comprehensive, but it increased our bundle size a good bit. StructuredClone, meanwhile, is too
  // naive.

  // Initialize our knownMap with Singletons.
  knownMap = knownMap ?? new Map<any, any>([
    [null, null],
    [NaN, NaN],
    [Infinity, Infinity],
    [window, window],
    [document, document]
  ])
  if (knownMap.has(item)) {
    return item
  }
  if (PRIMITIVES.has(typeof item)) {
    return item
  }
  if (Array.isArray(item)) {
    const result = []
    for (const entry of item) {
      if (!knownMap.has(entry)) {
        knownMap.set(entry, clone(entry, knownMap))
      }
      result.push(knownMap.get(entry) as typeof entry)
    }
    return result as T
  }
  if (item instanceof Set) {
    const result = new Set()
    for (const value of item.values()) {
      if (!knownMap.has(value)) {
        knownMap.set(value, clone(value, knownMap))
      }
      result.add(knownMap.get(value))
    }
    return result as T
  }
  if (item instanceof Map) {
    const result = new Map()
    for (const [key, value] of item.entries()) {
      if (!knownMap.has(key)) {
        knownMap.set(key, clone(key, knownMap))
      }
      if (!knownMap.has(value)) {
        knownMap.set(value, clone(value, knownMap))
      }
      result.set(knownMap.get(key), knownMap.get(value))
    }
    return result as T
  }
  const result: any = {};
  for (const [key, value] of Object.entries(item as Record<any, any>)) {
    if (!knownMap.has(value)) {
      knownMap.set(value, clone(value, knownMap))
    }
    result[key] = value
  }
  return result as T
}
