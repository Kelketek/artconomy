/* istanbul ignore file */
import {AxiosRequestConfig, AxiosResponse} from 'axios'
import {csrfSafeMethod, genId, getCookie, saneNav} from '@/lib/lib'
import {createLocalVue, mount as upstreamMount, ThisTypedMountOptions, VueClass, Wrapper} from '@vue/test-utils'
import Vue, {VueConstructor} from 'vue'
import {FieldController} from '@/store/forms/field-controller'
import {FieldBank} from '@/store/forms/form-controller'
import flushPromisesUpstream from 'flush-promises'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import {AnonUser} from '@/store/profiles/types/AnonUser'
import {User} from '@/store/profiles/types/User'
import {Ratings} from '@/store/profiles/types/Ratings'
import Vuex, {Store} from 'vuex'
import {ProfileModule} from '@/store/profiles'
import {SingleModule} from '@/store/singles'
import {
  artistProfileEndpointFor,
  artistProfilePathFor,
  endpointFor,
  pathFor,
  userPathFor,
} from '@/store/profiles/helpers'
import Vuetify from 'vuetify'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {listRegistry, Lists} from '@/store/lists/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import colors from 'vuetify/es5/util/colors'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import {characterRegistry, Characters} from '@/store/characters/registry'
import mockAxios from '@/__mocks__/axios'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ArtStore, createStore} from '@/store'
import Router from 'vue-router'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs'
import {Shortcuts} from '@/plugins/shortcuts'
import {useRealStorage} from '@/lib/specs/helpers'
import {VueSocket} from '@/plugins/socket'
import WS from 'jest-websocket-mock'
import Component, {mixins} from 'vue-class-component'

export interface ExtraData {
  status?: number,
  statusText?: string,
  headers?: { [key: string]: string },
  config?: AxiosRequestConfig,
}

export function rs(data: any, extra?: ExtraData): AxiosResponse {
  const extraData = extra || {}
  return {
    data,
    status: 200,
    statusText: 'OK',
    headers: {'Content-Type': 'application/json; charset=utf-8'},
    config: {},
    ...extraData,
  }
}

export function rq(url: string, method: HttpVerbs, data?: any, config?: { [key: string]: any }) {
  const starterHeaders: { [key: string]: string } = {'Content-Type': 'application/json; charset=utf-8'}
  config = config || {cancelToken: expect.any(Object)}
  if (!config.headers) {
    config.headers = {}
  }
  const token = getCookie('csrftoken')
  if (token && !csrfSafeMethod(method)) {
    starterHeaders['X-CSRFToken'] = token
  }
  config.headers = {...starterHeaders, ...config.headers}
  return [url, data, config]
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

export function fieldEl(wrapper: Wrapper<Vue>, field: FieldController) {
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

export function setViewer(store: Store<any>, user: User|AnonUser|TerseUser) {
  const username = user.username
  store.registerModule(pathFor(username), new ProfileModule({viewer: true}))
  store.registerModule(
    userPathFor(username),
    new SingleModule<User|AnonUser|TerseUser>({x: user, endpoint: endpointFor(username)}),
  )
  store.registerModule(
    artistProfilePathFor(username),
    new SingleModule<User|AnonUser|TerseUser>({x: null, endpoint: artistProfileEndpointFor(username)}),
  )
  store.commit('profiles/setViewerUsername', username)
  store.commit(`userModules/${username}/user/setReady`, true)
}

export function genAnon(overrides?: Partial<AnonUser>): AnonUser {
  return {
    rating: Ratings.GENERAL,
    blacklist: [],
    sfw_mode: false,
    username: '_',
    birthday: null,
    ...overrides,
  }
}

export async function confirmAction(wrapper: Wrapper<Vue>, selectors: string[]) {
  for (const selector of selectors) {
    wrapper.find(selector).trigger('click')
    await wrapper.vm.$nextTick()
  }
  wrapper.find('.v-dialog--active .confirmation-button').trigger('click')
}

export function makeSpace() {
  // Prints a bunch of lines to the console. Used to make sure Jest's test runner doesn't overwrite
  // useful information when it summarizes
  for (let index = 0; index < 10; index++) {
    console.log('***')
  }
}

export function vueSetup() {
  // Create a localVue with the most common parameters needed for testing our components.
  Vue.use(Vuex)
  Vue.use(Vuetify)
  const localVue = createLocalVue()
  localVue.use(VueSocket, {endpoint: 'ws://localhost/test/url'})
  localVue.use(Singles)
  localVue.use(Lists)
  localVue.use(Profiles)
  localVue.use(FormControllers)
  localVue.use(Characters)
  localVue.use(Shortcuts)
  vuetifySetup()
  // We won't use the Router in all tests, but we always have these modifications when we do.
  // @ts-ignore
  if (!Router.prototype.push.PATCHED) {
    // @ts-ignore
    Router.prototype.push = saneNav(Router.prototype.push)
    // @ts-ignore
    Router.prototype.replace = saneNav(Router.prototype.replace)
  }
  return localVue
}

export function createVuetify() {
  // @ts-ignore
  return new Vuetify({
    icons: {
      iconfont: 'mdiSvg',
    },
    theme: {
      dark: true,
      themes: {
        dark: {
          primary: colors.blue.base,
          secondary: colors.purple.base,
          danger: colors.red.base,
          darkBase: colors.grey.base,
        },
      },
    },
    options: {
      customProperties: true,
    },
  })
}

export function cleanUp(wrapper?: Wrapper<Vue>) {
  mockAxios.reset()
  jest.clearAllTimers()
  if (wrapper) {
    if (wrapper.vm.$sock) {
      wrapper.vm.$sock.reset()
    }
    wrapper.destroy()
  }
  WS.clean()
  singleRegistry.reset()
  profileRegistry.reset()
  listRegistry.reset()
  formRegistry.reset()
  characterRegistry.reset()
  useRealStorage()
}

export function setPricing(store: ArtStore, localVue: VueConstructor<Vue>) {
  const pricing = mount(Empty, {
    localVue, store,
  }).vm.$getSingle('pricing', {endpoint: '/pricing/'})
  pricing.setX({
    premium_percentage_bonus: 50,
    premium_static_bonus: 0.25,
    landscape_price: 5.00,
    standard_percentage: 8,
    standard_static: 0.75,
    portrait_price: 3.00,
    minimum_price: 1.10,
    table_percentage: 10,
    table_static: 5,
    table_tax: 8.25,
  })
  pricing.ready = true
  return pricing
}

export function timeout(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export async function sleep(fn: Function, ms: number, ...args: any[]) {
  await timeout(ms)
  return fn(...args)
}

export function docTarget() {
  const rootDiv = document.createElement('div')
  rootDiv.setAttribute('id', genId())
  document.querySelector('body')!.appendChild(rootDiv)
  return rootDiv
}

export function qMount<V extends Vue>(component: VueClass<V>, options?: ThisTypedMountOptions<V>): Wrapper<Vue> {
  return mount(component, prepTest(options))
}

export function prepTest<V extends Vue>(overrides?: Partial<ThisTypedMountOptions<V>>) {
  overrides = {...overrides}
  if (overrides.attachTo === undefined) {
    // Should fail if empty string, which is what we'll use to indicate non-attachment.
    overrides.attachTo = docTarget()
  } else if (overrides?.attachTo === '') {
    overrides.attachTo = undefined
  }
  return {
    localVue: overrides?.localVue || vueSetup(),
    store: overrides?.store || createStore(),
    vuetify: overrides?.vuetify || createVuetify(),
    ...overrides,
  }
}

export function mount<V extends Vue>(component: VueClass<V>, options?: ThisTypedMountOptions<V>): Wrapper<V> {
  // I'm not sure I'm going to need this. But it looked like I did once, and it was a pain in the ass to convert
  // everything over, so I'm keeping it.
  return upstreamMount(component, options)
}
