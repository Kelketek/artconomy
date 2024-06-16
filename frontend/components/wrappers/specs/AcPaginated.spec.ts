import {VueWrapper} from '@vue/test-utils'
import {cleanUp, createTestRouter, mount, sleep, vueSetup, waitFor} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {RouteLocationRaw, Router} from 'vue-router'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'
import {nextTick} from 'vue'

let wrapper: VueWrapper<any>
let store: ArtStore
let router: Router
let route: Partial<RouteLocationRaw>

describe('AcPaginated.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = createTestRouter()
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
        router,
      }),
      props: {
        list: paginatedList,
        autoRun: false,
      },
    })
    expect(paginatedList.fetching).toBe(false)
  })
  test('Updates the router when changing pages', async() => {
    await router.push('/?stuff=things')
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
        router,
      }),
      props: {
        list: paginatedList,
        trackPages: true,
      },
    })
    paginatedList.currentPage = 2
    await waitFor(() => expect(router.currentRoute.value.query.page).toEqual('2'))
    expect(router.currentRoute.value.query.stuff).toEqual('things')
  })
  test('Does not update the router if told not to', async() => {
    await router.push('/')
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
        router,
      }),
      props: {list: paginatedList},
    })
    paginatedList.currentPage = 2
    await nextTick()
    await sleep(1000)
    expect(router.currentRoute.value.query).toEqual({})
  })
  test('Loads the right page to start', async() => {
    await router.push('/?page=2')
    const paginatedList = mount(
      Empty, vueSetup({store}),
    ).vm.$getList('stuff', {endpoint: '/wat/'})
    wrapper = mount(AcPaginated, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        list: paginatedList,
        trackPages: true,
      },
    })
    await nextTick()
    expect(paginatedList.currentPage).toBe(2)
  })
})
