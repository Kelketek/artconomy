import {cleanUp, createVuetify, docTarget, setViewer, vueSetup, mount} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import {Vue} from 'vue/types/vue'
import {ArtStore, createStore} from '@/store'
import Home from '@/components/views/Home.vue'
import {genUser} from '@/specs/helpers/fixtures'
import searchSchema from '@/components/views/search/specs/fixtures'
import {FormController} from '@/store/forms/form-controller'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let searchForm: FormController
let vuetify: Vuetify

describe('Home.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    searchForm = mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, {localVue, store, vuetify, mocks: {$router: {}}, stubs: ['router-link']})
  })
  it('Handles several lists', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, {localVue, store, vuetify, mocks: {$router: {}}, stubs: ['router-link']})
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
  it('Performs a premade search for products', async() => {
    setViewer(store, genUser())
    const push = jest.fn()
    wrapper = mount(Home, {localVue, store, vuetify, mocks: {$router: {push}}, stubs: ['router-link'], attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    wrapper.findAll('.v-tab').at(2).trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    wrapper.find('.low-price-more').trigger('click')
    await wrapper.vm.$nextTick()
    expect(push).toHaveBeenCalledWith({name: 'SearchProducts', query: {max_price: '30.00', page: '1', size: '24'}})
  })
  it('Performs a search for characters', async() => {
    setViewer(store, genUser())
    const push = jest.fn()
    wrapper = mount(Home, {
      localVue, store, vuetify, mocks: {$router: {push}}, stubs: ['router-link'], attachTo: docTarget(),
    })
    searchForm.fields.q.update('test')
    wrapper.find('.search-characters').trigger('click')
    await wrapper.vm.$nextTick()
    expect(push).toHaveBeenCalledWith({name: 'SearchCharacters', query: {page: '1', size: '24'}})
    expect(searchForm.fields.q.value).toBe('')
  })
  it('Performs a search for submissions', async() => {
    setViewer(store, genUser())
    const push = jest.fn()
    wrapper = mount(Home, {localVue, store, vuetify, mocks: {$router: {push}}, stubs: ['router-link']})
    searchForm.fields.q.update('test')
    await wrapper.vm.$nextTick()
    wrapper.find('.search-submissions').trigger('click')
    await wrapper.vm.$nextTick()
    expect(push).toHaveBeenCalledWith({name: 'SearchSubmissions', query: {page: '1', size: '24'}})
    expect(searchForm.fields.q.value).toBe('')
  })
  it('Performs a search for Products', async() => {
    setViewer(store, genUser())
    const push = jest.fn()
    wrapper = mount(
      Home,
      {
        localVue,
        store,
        vuetify,
        mocks: {$router: {push}},
        stubs: ['router-link'],
        attachTo: docTarget(),
      })
    searchForm.fields.q.update('test')
    await wrapper.vm.$nextTick()
    wrapper.find('.home-search-field input').trigger('keyup')
    await wrapper.vm.$nextTick()
    expect(push).toHaveBeenCalledWith({name: 'SearchProducts', query: {page: '1', size: '24', q: 'test'}})
  })
})
