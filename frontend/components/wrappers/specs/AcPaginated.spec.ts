import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {vuetifySetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {characterRegistry, Characters} from '@/store/characters/registry'
import {listRegistry, Lists} from '@/store/lists/registry'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {Route} from 'vue-router/types/router'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Profiles)
localVue.use(Lists)
localVue.use(Characters)
localVue.use(FormControllers)
let wrapper: Wrapper<Vue>
let store: ArtStore
let router: any
let route: Partial<Route>

describe('AcPaginated.vue', () => {
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    profileRegistry.reset()
    characterRegistry.reset()
    listRegistry.reset()
    formRegistry.reset()
    route = {
      query: {stuff: 'things'},
    }
    router = {
      replace: jest.fn(),
    }
  })
  it('Loads a paginated list', () => {
    const paginatedList = mount(Empty, {localVue, store}).vm.$getList('stuff', {endpoint: '/wat/'})
    const firstPage = []
    for (let i = 1; i <= 10; i++) {
      const sub = genSubmission()
      sub.id = i
      firstPage.push(sub)
    }
    paginatedList.setList(firstPage)
    paginatedList.response = ({size: 10, count: 30})
    wrapper = mount(AcPaginated, {localVue, store, propsData: {list: paginatedList}})
  })
  it('Does not load a list initially if autoRun is false', () => {
    const paginatedList = mount(Empty, {localVue, store}).vm.$getList('stuff', {endpoint: '/wat/'})
    wrapper = mount(AcPaginated, {
      localVue, store, propsData: {list: paginatedList, autoRun: false}, sync: false, attachToDocument: true,
    })
    expect(paginatedList.fetching).toBe(false)
  })
  it('Updates the router when changing pages', async() => {
    const paginatedList = mount(
      Empty, {localVue, store}
    ).vm.$getList('stuff', {endpoint: '/wat/'})
    const firstPage = []
    for (let i = 1; i <= 10; i++) {
      const sub = genSubmission()
      sub.id = i
      firstPage.push(sub)
    }
    paginatedList.setList(firstPage)
    paginatedList.response = ({size: 10, count: 30})
    wrapper = mount(AcPaginated, {
      localVue,
      store,
      propsData: {list: paginatedList, trackPages: true},
      sync: false,
      attachToDocument: true,
      mocks: {$router: router, $route: route},
    })
    paginatedList.currentPage = 2
    await wrapper.vm.$nextTick()
    expect(router.replace).toHaveBeenCalledWith({query: {page: '2', stuff: 'things'}})
  })
  it('Does not update the router if told not to', async() => {
    const paginatedList = mount(
      Empty, {localVue, store}
    ).vm.$getList('stuff', {endpoint: '/wat/'})
    const firstPage = []
    for (let i = 1; i <= 10; i++) {
      const sub = genSubmission()
      sub.id = i
      firstPage.push(sub)
    }
    paginatedList.setList(firstPage)
    paginatedList.response = ({size: 10, count: 30})
    wrapper = mount(AcPaginated, {
      localVue,
      store,
      propsData: {list: paginatedList},
      sync: false,
      attachToDocument: true,
      mocks: {$router: router, $route: route},
    })
    paginatedList.currentPage = 2
    await wrapper.vm.$nextTick()
    expect(router.replace).not.toHaveBeenCalled()
  })
  it('Loads the right page to start', async() => {
    const paginatedList = mount(
      Empty, {localVue, store}
    ).vm.$getList('stuff', {endpoint: '/wat/'})
    // @ts-ignore
    route.query.page = '2'
    wrapper = mount(AcPaginated, {
      localVue,
      store,
      propsData: {list: paginatedList, trackPages: true},
      sync: false,
      attachToDocument: true,
      mocks: {$router: router, $route: route},
    })
    await wrapper.vm.$nextTick()
    expect(paginatedList.currentPage).toBe(2)
  })
})
