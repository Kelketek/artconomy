import {cleanUp, genAnon, mount, setViewer, vueSetup} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import Home from '@/components/views/Home.vue'
import {genUser} from '@/specs/helpers/fixtures.ts'
import searchSchema from '@/components/views/search/specs/fixtures.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore
let searchForm: FormController

describe('Home.vue', () => {
  beforeEach(() => {
    store = createStore()
    searchForm = mount(Empty, vueSetup({store})).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, vueSetup({
      store,
      mocks: {$router: {}},
      stubs: ['router-link'],
    }))
  })
  test('Handles several lists', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, vueSetup({
      store,
      mocks: {$router: {}},
      stubs: ['router-link'],
    }))
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
    vm.newArtistProducts.setList([])
    vm.newArtistProducts.ready = true
    vm.newArtistProducts.fetching = false
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
    await vm.$nextTick()
  })
  test('Performs a premade search for products', async() => {
    setViewer(store, genUser())
    const push = vi.fn()
    wrapper = mount(Home, vueSetup({
      store,
      mocks: {$router: {push}},
      stubs: ['router-link'],
    }))
    await wrapper.vm.$nextTick()
    await wrapper.findAll('.v-tab').at(2)!.trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    await wrapper.find('.low-price-more').trigger('click')
    await wrapper.vm.$nextTick()
    expect(push).toHaveBeenCalledWith({
      name: 'SearchProducts',
      query: {
        max_price: '30.00',
        page: '1',
        size: '24',
      },
    })
  })
  test('Performs a search for characters', async() => {
    setViewer(store, genUser())
    const push = vi.fn()
    wrapper = mount(Home, vueSetup({
      store,
      mocks: {$router: {push}},
      stubs: ['router-link'],
    }))
    searchForm.fields.q.update('test')
    await wrapper.find('.search-characters').trigger('click')
    await wrapper.vm.$nextTick()
    expect(push).toHaveBeenCalledWith({
      name: 'SearchCharacters',
      query: {
        page: '1',
        size: '24',
      },
    })
    expect(searchForm.fields.q.value).toBe('')
  })
  test('Performs a search for submissions', async() => {
    setViewer(store, genUser())
    const push = vi.fn()
    wrapper = mount(Home, vueSetup({
      store,
      mocks: {$router: {push}},
      stubs: ['router-link'],
    }))
    searchForm.fields.q.update('test')
    await wrapper.vm.$nextTick()
    await wrapper.find('.search-submissions').trigger('click')
    await wrapper.vm.$nextTick()
    expect(push).toHaveBeenCalledWith({
      name: 'SearchSubmissions',
      query: {
        page: '1',
        size: '24',
      },
    })
    expect(searchForm.fields.q.value).toBe('')
  })
  test('Performs a search for Products', async() => {
    setViewer(store, genAnon())
    const push = vi.fn()
    wrapper = mount(Home, vueSetup({
      store,
      mocks: {$router: {push}},
      stubs: ['router-link'],
    }))
    searchForm.fields.q.update('test')
    await wrapper.vm.$nextTick()
    wrapper.find('.home-search-field input').trigger('keyup')
    await wrapper.vm.$nextTick()
    expect(push).toHaveBeenCalledWith({
      name: 'SearchProducts',
      query: {
        page: '1',
        size: '24',
        q: 'test',
      },
    })
  })
})
