/* istanbul ignore file */
import {AxiosRequestConfig, AxiosResponse} from 'axios'
import {csrfSafeMethod, getCookie, saneNav} from '@/lib'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
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
import {ArtStore} from '@/store'
import Router from 'vue-router'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs'

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
  config = config || {cancelToken: {}}
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
    new SingleModule<User|AnonUser|TerseUser>({x: user, endpoint: endpointFor(username)})
  )
  store.registerModule(
    artistProfilePathFor(username),
    new SingleModule<User|AnonUser|TerseUser>({x: null, endpoint: artistProfileEndpointFor(username)})
  )
  store.commit('profiles/setViewerUsername', username)
  store.commit(`userModules/${username}/user/setReady`, true)
}

export function genAnon(): AnonUser {
  return {rating: Ratings.GENERAL, blacklist: [], sfw_mode: false, username: '_'}
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
  Vue.use(Vuetify, {
    theme: {
      primary: colors.blue,
      secondary: colors.purple,
      danger: colors.red,
      darkBase: colors.grey,
    },
    options: {
      customProperties: true,
    },
  })
  const localVue = createLocalVue()
  localVue.use(Singles)
  localVue.use(Lists)
  localVue.use(Profiles)
  localVue.use(FormControllers)
  localVue.use(Characters)
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

export function cleanUp(wrapper?: Wrapper<Vue>) {
  if (wrapper) {
    wrapper.destroy()
  }
  singleRegistry.reset()
  profileRegistry.reset()
  listRegistry.reset()
  formRegistry.reset()
  characterRegistry.reset()
  mockAxios.reset()
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
  })
  pricing.ready = true
  return pricing
}
