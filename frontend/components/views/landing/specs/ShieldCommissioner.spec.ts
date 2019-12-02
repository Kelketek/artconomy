import Vue from 'vue'
import Router from 'vue-router'
import {cleanUp, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import searchSchema from '@/components/views/search/specs/fixtures'
import {FormController} from '@/store/forms/form-controller'
import ShieldCommissioner from '@/components/views/landing/ShieldCommissioner.vue'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let searchForm: FormController
let router: Router

describe('Shield.vue', () => {
  beforeEach(() => {
    store = createStore()
    searchForm = mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'SearchProducts',
        path: '/search/products/',
        component: Empty,
      }, {
        name: 'BuyAndSell',
        path: '/faq/buy-and-sell/',
        component: Empty,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Calls Search', async() => {
    const wrapper = mount(ShieldCommissioner, {localVue, store, router, attachToDocument: true, sync: false})
    wrapper.find('.commission-cta').trigger('click')
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.name).toBe('SearchProducts')
    expect(router.currentRoute.query).toEqual({shield_only: true})
  })
})