/* istanbul ignore file */
import type {AxiosRequestConfig, AxiosResponse} from 'axios'
import {AxiosHeaders} from 'axios'
import {expect, vi} from 'vitest'
import VueMask from '@devindex/vue-mask'
import {csrfSafeMethod, genId, getCookie, immediate} from '@/lib/lib.ts'
import {mount as upstreamMount, VueWrapper} from '@vue/test-utils'
import {ComponentPublicInstance, defineComponent} from 'vue'
import {FieldController} from '@/store/forms/field-controller.ts'
import {FieldBank} from '@/store/forms/form-controller.ts'
import flushPromisesUpstream from 'flush-promises'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
import {Ratings} from '@/store/profiles/types/Ratings.ts'
import {createSingles, singleRegistry} from '@/store/singles/registry.ts'
import {createLists, listRegistry} from '@/store/lists/registry.ts'
import {createProfiles, profileRegistry} from '@/store/profiles/registry.ts'
import {createForms, formRegistry} from '@/store/forms/registry.ts'
import {characterRegistry, createCharacters} from '@/store/characters/registry.ts'
import mockAxios from '@/__mocks__/axios.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs.ts'
import {Shortcuts} from '@/plugins/shortcuts.ts'
import WS from 'vitest-websocket-mock'
import {genPricing} from '@/lib/specs/helpers.ts'
import {createVuetify as upstreamCreateVuetify} from 'vuetify'
import {createVueSocket} from '@/plugins/socket.ts'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import {createTargetsPlugin} from '@/plugins/targets.ts'
import {createRegistries} from '@/plugins/createRegistries.ts'
import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import {routes} from '@/router'

export interface ExtraData {
  status?: number,
  statusText?: string,
  headers?: { [key: string]: string },
  config?: {headers: AxiosHeaders},
}

export const createVuetify = upstreamCreateVuetify

export function rs(data: any, extra?: ExtraData): AxiosResponse {
  const extraData = extra || {}
  return {
    data,
    status: 200,
    statusText: 'OK',
    headers: {'Content-Type': 'application/json; charset=utf-8'},
    config: {headers: new AxiosHeaders({})},
    ...extraData,
  }
}

export function rq(url: string, method: HttpVerbs, data?: any, config?: AxiosRequestConfig) {
  const starterHeaders: { [key: string]: string } = {'Content-Type': 'application/json; charset=utf-8'}
  config = config || {signal: expect.any(Object)}
  if (!config.headers) {
    config.headers = {}
  }
  const token = getCookie('csrftoken')
  if (token && !csrfSafeMethod(method)) {
    starterHeaders['X-CSRFToken'] = token
  }
  config.headers = {...starterHeaders, ...config.headers}
  return {
    url,
    data,
    method,
    ...config,
  }
}

export function dialogExpects(spec: { wrapper: any, formName: string, fields: string[] }) {
  const wrapper = spec.wrapper
  const formName = spec.formName
  const fields = spec.fields
  const dialogue = wrapper.find(`#form-${formName}`)
  expect(dialogue.exists()).toBeTruthy()
  for (const field of fields) {
    expect(dialogue.find(`#field-${formName}__${field}`).exists()).toBeTruthy()
  }
  const submit = dialogue.find('.dialog-submit')
  expect(submit.exists()).toBeTruthy()
  return submit
}

export function vuetifySetup() {
  const el = document.createElement('div')
  el.setAttribute('data-app', 'true')
  document.body.appendChild(el)
}

export function fieldEl(wrapper: VueWrapper<any>, field: FieldController) {
  const el = wrapper.find('#' + field.id)
  if (!el.exists()) {
    throw Error(`Could not find ${'#' + field.id}`)
  }
  return el.element as HTMLInputElement
}

export function expectFields(fieldSet: FieldBank, names: string[]) {
  for (const name of names) {
    expect(fieldSet[name]).toBeTruthy()
  }
}

export const flushPromises = flushPromisesUpstream

export function genAnon(overrides?: Partial<AnonUser>): AnonUser {
  return {
    rating: Ratings.GENERAL,
    blacklist: [],
    nsfw_blacklist: [],
    sfw_mode: false,
    username: '_',
    birthday: null,
    ...overrides,
  }
}

export async function confirmAction(wrapper: VueWrapper<any>, selectors: string[]) {
  for (const selector of selectors) {
    try {
      await waitFor(() => wrapper.find(selector).trigger('click'))
    } catch (e) {
      console.log(`Could not find ${selector} in`, wrapper.html())
      throw e
    }
  }
  try {
    await waitFor(() => wrapper.find('.v-overlay--active .confirmation-button').trigger('click'))
  } catch (e) {
    console.log(wrapper.html())
    throw e
  }
}

export function makeSpace() {
  // Prints a bunch of lines to the console. Used to make sure Jest's test runner doesn't overwrite
  // useful information when it summarizes
  for (let index = 0; index < 10; index++) {
    console.log('***')
  }
}

export type VueMountOptions = {
  global: {
    plugins: any[],
    stubs?: string[] | Record<string, ReturnType<typeof defineComponent>>,
    mocks?: {[key: string]: any},
    components?: Record<string, ReturnType<typeof defineComponent> | object>,
  },
  attachTo: string | HTMLElement,
}

export type MountOverrideOptions = {
  store?: ArtStore,
  vuetify?: ReturnType<typeof createVuetify>
  socket?: ReturnType<typeof createVueSocket>
  extraPlugins?: any[],
  stubs?: string[] | Record<string, ReturnType<typeof defineComponent>>,
  mocks?: {[key: string]: any},
  attachTo?: string | HTMLElement,
  components?: Record<string, ReturnType<typeof defineComponent> | object>,
}

export function vueSetup(overrides?: MountOverrideOptions): VueMountOptions {
  overrides = overrides || {}
  // Create a localVue with the most common parameters needed for testing our components.
  const store = overrides.store || createStore()
  return {
    global: {
      stubs: overrides.stubs,
      components: overrides.components,
      mocks: overrides.mocks,
      plugins: [
        store,
        createSingles(store),
        createLists(store),
        createProfiles(store),
        createForms(store),
        createCharacters(store),
        createRegistries(),
        VueMask,
        Shortcuts,
        createTargetsPlugin(true),
        overrides.socket || createVueSocket({endpoint: `ws://localhost/test/url/${genId()}`}),
        overrides.vuetify || createVuetify({
          components,
          directives,
        }),
        ...(overrides.extraPlugins || []),
      ]},
    attachTo: overrides.attachTo || docTarget(),
  }
}

export function createDocumentTargets() {
  let el = document.createElement('div')
  el.id = 'modal-target'
  document.body.appendChild(el)
  el = document.createElement('div')
  el.id = 'snackbar-target'
  document.body.appendChild(el)
}

export function cleanUp(wrapper?: VueWrapper<any>) {
  mockAxios.reset()
  vi.clearAllTimers()
  if (wrapper) {
    if (wrapper.vm && wrapper.vm.$sock) {
      wrapper.vm.$sock.reset()
    }
    wrapper.unmount()
  }
  WS.clean()
  singleRegistry.reset()
  profileRegistry.reset()
  listRegistry.reset()
  formRegistry.reset()
  characterRegistry.reset()
  localStorage.clear()
}

// The TS-ignores are here because there's no sane way to populate this wrapper
// with class-based Vue objects, as far as I know. Revisit once converted to
// functional components.
export function setPricing(store: ArtStore) {
  const pricing: VueWrapper<any> = mount(Empty, vueSetup({
    store,
  })).vm.$getSingle('pricing', {endpoint: '/pricing/'})
  // @ts-ignore
  pricing.setX(genPricing())
  // @ts-ignore
  pricing.ready = true
  return pricing
}

export function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export function docTarget() {
  const rootDiv = document.createElement('div')
  rootDiv.setAttribute('id', genId())
  document.body.appendChild(rootDiv)
  return rootDiv
}

export function qMount<V>(component: ComponentPublicInstance<V>, options?: any): VueWrapper<any> {
  return mount(component, options)
}

// At one point it looked like everything needed to be moved over to a wrapped version of the upstream mount
// function. This turned out not to be the case, but it was not easy to roll back and I might need it eventually,
// so it's reexported here.
export const mount = <T>(component: T, options: any): VueWrapper<any> => upstreamMount(component, options)

export const mockCardMount = vi.fn()
export const mockCardCreate = vi.fn()
export const mockStripe = () => {
  const stripeInstance = {
    elements: () => {
      return {
        create: mockCardCreate,
      }
    },
    confirmCardPayment: async() => {
      return immediate(stripeInstance.paymentValue)
    },
    confirmCardSetup: async() => {
      return immediate(stripeInstance.setupValue)
    },
    reset() {
      stripeInstance.setupValue = null
      stripeInstance.paymentValue = null
    },
    setupValue: null as any,
    // Set this to whatever you want confirmCardPayment to return.
    paymentValue: null as any,
  }
  return stripeInstance
}

export function VuetifyWrapped(component: ReturnType<typeof defineComponent>) {
  return defineComponent({
    components: {wrapped: component},
    inheritAttrs: false,
    template: '<v-app><wrapped v-bind="{...$attrs, ...additional}" ref="vm"/><div id="modal-target" /><div id="snackbar-target" /><div id="menu-target" /></v-app>',
    props: ['id'],
    computed: {
      additional() {
        return this.id ? {id: this.id} : {}
      }
    }
  })
}

export const realTimerScope = (): () => void => {
  // Ensures that real timers are used, and returns a function to be called when whatever they are needed
  // for is finished, which will restore the fake timers if they were used.
  if (vi.isFakeTimers()) {
    vi.useRealTimers()
    return () => vi.useFakeTimers()
  }
  return () => {}
}

export async function waitFor(func: () => any, timeout = 1000) {
  const restoreFakes = realTimerScope()
  const startTime = Date.now()
  // eslint-disable-next-line no-constant-condition
  while (true) {
    try {
      const result = await func()
      restoreFakes()
      return result
    } catch (e) {
      if ((Date.now() - startTime) >= timeout) {
        restoreFakes()
        throw e
      }
    }
    await sleep(50)
  }
}

export const nullifyRoutes = (routeArray: RouteRecordRaw[]): RouteRecordRaw[] => {
  // Takes all given routes and replaces them with the bogus (and cheaply instantiated) Empty component.
  return routeArray.map((oldRoute: RouteRecordRaw) => {
    const route = {...oldRoute}
    if (route.component !== undefined) {
      route.component = Empty
    }
    if (route.children && route.children.length) {
      route.children = nullifyRoutes(route.children)
    }
    return route
  })
}

export const mockRoutes = nullifyRoutes(routes)

export const createTestRouter = (quick = true) => {
  let routes: RouteRecordRaw[]
  if (quick) {
    routes = [{name: 'Home', component: Empty, path: '/'}]
  } else {
    routes = mockRoutes
  }
  return createRouter({
    history: createWebHistory(),
    routes,
  })
}

export const waitForSelector = async (wrapper: VueWrapper, selector: string) => {
  return await waitFor(() => expect(wrapper.find(selector).exists()).toBe(true))
}

export const mockStripeInitializer = vi.fn()
mockStripeInitializer.mockImplementation(mockStripe)
mockCardCreate.mockImplementation(() => ({mount: mockCardMount}))
window.Stripe = mockStripeInitializer
