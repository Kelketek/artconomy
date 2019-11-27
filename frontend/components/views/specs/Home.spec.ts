import {setViewer, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import {Vue} from 'vue/types/vue'
import {ArtStore, createStore} from '@/store'
import Home from '@/components/views/Home.vue'
import {genUser} from '@/specs/helpers/fixtures'
import searchSchema from '@/components/views/search/specs/fixtures'
import {FormController} from '@/store/forms/form-controller'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let searchForm: FormController

describe('Home.vue', () => {
  beforeEach(() => {
    store = createStore()
    searchForm = mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    wrapper.destroy()
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, {localVue, store, mocks: {$router: {}}, stubs: ['router-link']})
  })
  it('Handles several lists', async() => {
    setViewer(store, genUser())
    wrapper = mount(Home, {localVue, store, mocks: {$router: {}}, stubs: ['router-link']})
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
    await vm.$nextTick()
  })
  it('Performs a premade search', async() => {
    setViewer(store, genUser())
    const push = jest.fn()
    wrapper = mount(Home, {localVue, store, mocks: {$router: {push}}, stubs: ['router-link']})
    wrapper.find('.low-price-more').trigger('click')
    await wrapper.vm.$nextTick()
    expect(push).toHaveBeenCalledWith({name: 'SearchProducts', query: {max_price: '30.00'}})
  })
})
