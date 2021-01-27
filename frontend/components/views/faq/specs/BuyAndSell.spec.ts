import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Router from 'vue-router'
import {faqRoutes} from './helpers'
import {Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import BuyAndSell from '@/components/views/faq/BuyAndSell.vue'
import {cleanUp, createVuetify, docTarget, setPricing, vueSetup, mount} from '@/specs/helpers'
import searchSchema from '@/components/views/search/specs/fixtures'
import {FormController} from '@/store/forms/form-controller'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {createPinterestQueue} from '@/lib/lib'

const localVue = vueSetup()
localVue.use(Router)
let searchForm: FormController

describe('About.vue', () => {
  let router: Router
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  let vuetify: Vuetify
  beforeEach(() => {
    router = new Router(faqRoutes)
    store = createStore()
    vuetify = createVuetify()
    searchForm = mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
    window.pintrk = createPinterestQueue()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Shows the buy and sell FAQ', async() => {
    await router.push('/faq/buying-and-selling/')
    wrapper = mount(BuyAndSell, {localVue, router, store, vuetify, attachTo: docTarget()})
    const vm = wrapper.vm as any
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.params).toEqual({question: 'how-to-buy'})
    setPricing(store, localVue)
    await vm.$nextTick()
  })
  it('Sends the user to search', async() => {
    searchForm.fields.q.update('stuff', false)
    await router.push('/faq/buying-and-selling/')
    wrapper = mount(BuyAndSell, {localVue, router, store, vuetify, attachTo: docTarget()})
    const vm = wrapper.vm as any
    await wrapper.vm.$nextTick()
    wrapper.find('.who-is-open-link').trigger('click')
    await vm.$nextTick()
    expect(router.currentRoute.name).toBe('SearchProducts')
    expect(searchForm.fields.q.model).toBe('')
  })
})
