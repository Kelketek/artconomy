import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {RouteLocationRaw} from 'vue-router'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore
let router: any
let route: Partial<RouteLocationRaw>

describe('AcPaginated.vue', () => {
  beforeEach(() => {
    store = createStore()
    route = {
      query: {stuff: 'things'},
    }
    router = {
      replace: vi.fn(),
    }
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Loads a paginated list', async() => {
    const paginatedList = mount(Empty, vueSetup({
      store,
    })).vm.$getList('stuff', {endpoint: '/wat/'})
    const firstPage = []
    for (let i = 1; i <= 10; i++) {
      const sub = genSubmission()
      sub.id = i
      firstPage.push(sub)
    }
    paginatedList.setList(firstPage)
    paginatedList.response = ({
      size: 10,
      count: 30,
    })
    wrapper = mount(AcPaginated, {
      ...vueSetup({
        store,
      }),
      props: {list: paginatedList},
    })
  })
  test('Does not load a list initially if autoRun is false', () => {
    const paginatedList = mount(Empty, vueSetup(vueSetup({store}))).vm.$getList('stuff', {endpoint: '/wat/'})
    wrapper = mount(AcPaginated, {
      ...vueSetup({
        store,
      }),
      props: {
        list: paginatedList,
        autoRun: false,
      },
    })
    expect(paginatedList.fetching).toBe(false)
  })
  test('Updates the router when changing pages', async() => {
    const paginatedList = mount(
      Empty, vueSetup({store}),
    ).vm.$getList('stuff', {endpoint: '/wat/'})
    const firstPage = []
    for (let i = 1; i <= 10; i++) {
      const sub = genSubmission()
      sub.id = i
      firstPage.push(sub)
    }
    paginatedList.setList(firstPage)
    paginatedList.response = ({
      size: 10,
      count: 30,
    })
    wrapper = mount(AcPaginated, {
      ...vueSetup({
        store,
        mocks: {
          $router: router,
          $route: route,
        },
      }),
      props: {
        list: paginatedList,
        trackPages: true,
      },
    })
    paginatedList.currentPage = 2
    await wrapper.vm.$nextTick()
    expect(router.replace).toHaveBeenCalledWith({
      query: {
        page: '2',
        stuff: 'things',
      },
    })
  })
  test('Does not update the router if told not to', async() => {
    const paginatedList = mount(
      Empty, vueSetup({store}),
    ).vm.$getList('stuff', {endpoint: '/wat/'})
    const firstPage = []
    for (let i = 1; i <= 10; i++) {
      const sub = genSubmission()
      sub.id = i
      firstPage.push(sub)
    }
    paginatedList.setList(firstPage)
    paginatedList.response = ({
      size: 10,
      count: 30,
    })
    wrapper = mount(AcPaginated, {
      ...vueSetup({
        store,
        mocks: {
          $router: router,
          $route: route,
        },
      }),
      props: {list: paginatedList},
    })
    paginatedList.currentPage = 2
    await wrapper.vm.$nextTick()
    expect(router.replace).not.toHaveBeenCalled()
  })
  test('Loads the right page to start', async() => {
    const paginatedList = mount(
      Empty, vueSetup({store}),
    ).vm.$getList('stuff', {endpoint: '/wat/'})
    // @ts-ignore
    route.query.page = '2'
    wrapper = mount(AcPaginated, {
      ...vueSetup({
        store,
        mocks: {
          $router: router,
          $route: route,
        },
      }),
      props: {
        list: paginatedList,
        trackPages: true,
      },
    })
    await wrapper.vm.$nextTick()
    expect(paginatedList.currentPage).toBe(2)
  })
})
