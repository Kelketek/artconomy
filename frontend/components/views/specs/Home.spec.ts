import {cleanUp, createTestRouter, mount, vueSetup} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import Home from '@/components/views/Home.vue'
import {genAnon, genUser} from '@/specs/helpers/fixtures.ts'
import searchSchema from '@/components/views/search/specs/fixtures.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {Router} from 'vue-router'
import {nextTick} from 'vue'
import {setViewer} from '@/lib/lib.ts'

let wrapper: VueWrapper<any>
let store: ArtStore
let searchForm: FormController
let router: Router

describe('Home.vue', () => {
  beforeEach(() => {
    store = createStore()
    searchForm = mount(Empty, vueSetup({store})).vm.$getForm('search', searchSchema())
    router = createTestRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, vueSetup({
      store,
      router,
      stubs: ['router-link'],
    }))
    await nextTick()
  })
  test('Handles several lists', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, vueSetup({
      store,

      stubs: ['router-link'],
    }))
    await nextTick()
    const vm = wrapper.vm as any
    vm.featured.setList([])
    vm.featured.ready = true
    vm.featured.fetching = false
    vm.rated.setList([])
    vm.rated.ready = true
    vm.rated.fetching = false
    vm.lowPriced.setList([])
    vm.lowPriced.ready = true
    vm.lowPriced.fetching = false
    vm.randomProducts.setList([])
    vm.randomProducts.ready = true
    vm.randomProducts.fetching = false
    vm.commissions.setList([])
    vm.commissions.ready = true
    vm.commissions.fetching = false
    vm.submissions.setList([])
    vm.submissions.ready = true
    vm.submissions.fetching = false
    vm.characters.setList([])
    vm.characters.ready = true
    vm.characters.fetching = false
    await nextTick()
  })
  test('Performs a premade search for products', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, vueSetup({
      store,
      router,
      stubs: ['router-link'],
    }))
    await nextTick()
    await nextTick()
    await wrapper.findAll('.v-tab').at(2)!.trigger('click')
    await nextTick()
    await nextTick()
    await wrapper.find('.low-price-more').trigger('click')
    await nextTick()
    await router.isReady()
    expect(router.currentRoute.value.name).toEqual('SearchProducts')
    expect(router.currentRoute.value.query).toEqual({
      max_price: '30.00',
      page: '1',
      size: '24',
    })
  })
  test('Performs a search for characters', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, vueSetup({
      store,
      router,
      stubs: ['router-link'],
    }))
    await nextTick()
    searchForm.fields.q.update('test')
    await wrapper.find('.search-characters').trigger('click')
    await nextTick()
    await router.isReady()
    expect(router.currentRoute.value.name).toEqual('SearchCharacters')
    expect(router.currentRoute.value.query).toEqual({
      page: '1',
      size: '24',
    })
    expect(searchForm.fields.q.value).toBe('')
  })
  test('Performs a search for submissions', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, vueSetup({
      store,
      router,
      stubs: ['router-link'],
    }))
    await nextTick()
    searchForm.fields.q.update('test')
    await nextTick()
    await wrapper.find('.search-submissions').trigger('click')
    await nextTick()
    await router.isReady()
    expect(router.currentRoute.value.name).toEqual('SearchSubmissions')
    expect(router.currentRoute.value.query).toEqual({
      page: '1',
      size: '24',
    })
    expect(searchForm.fields.q.value).toBe('')
  })
  test('Performs a search for Products', async() => {
    setViewer(store, genAnon())
    wrapper = mount(Home, vueSetup({
      store,
      router,
      stubs: ['router-link'],
    }))
    await nextTick()
    searchForm.fields.q.update('test')
    await nextTick()
    await wrapper.find('.home-search-field input').trigger('keyup')
    await nextTick()
    await router.isReady()
    expect(router.currentRoute.value.name).toEqual('SearchProducts')
    expect(router.currentRoute.value.query).toEqual({
      page: '1',
      size: '24',
      q: 'test',
    })
  })
})
