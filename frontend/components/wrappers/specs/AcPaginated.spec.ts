import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {Route} from 'vue-router/types/router'
import {Vuetify} from 'vuetify/types'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let router: any
let route: Partial<Route>
let vuetify: Vuetify

describe('AcPaginated.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    route = {
      query: {stuff: 'things'},
    }
    router = {
      replace: jest.fn(),
    }
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Loads a paginated list', async() => {
    const paginatedList = mount(Empty, {
      localVue,
      store,
      sync: false,
    }).vm.$getList('stuff', {endpoint: '/wat/'})
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
      vuetify,
      propsData: {list: paginatedList},
    })
  })
  it('Does not load a list initially if autoRun is false', () => {
    const paginatedList = mount(Empty, {localVue, store}).vm.$getList('stuff', {endpoint: '/wat/'})
    wrapper = mount(AcPaginated, {
      localVue,
      store,
      vuetify,
      propsData: {list: paginatedList, autoRun: false},
      sync: false,
      attachToDocument: true,
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
      vuetify,
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
      vuetify,
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
      vuetify,
      propsData: {list: paginatedList, trackPages: true},
      sync: false,
      attachToDocument: true,
      mocks: {$router: router, $route: route},
    })
    await wrapper.vm.$nextTick()
    expect(paginatedList.currentPage).toBe(2)
  })
})
