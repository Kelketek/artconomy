import Vue from 'vue'
import Router from 'vue-router'
import {faqRoutes} from './helpers'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import BuyAndSell from '@/components/views/faq/BuyAndSell.vue'
import {cleanUp, setPricing, vueSetup} from '@/specs/helpers'
import searchSchema from '@/components/views/search/specs/fixtures'
import {FormController} from '@/store/forms/form-controller'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
localVue.use(Router)
let searchForm: FormController

describe('About.vue', () => {
  let router: Router
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  beforeEach(() => {
    router = new Router(faqRoutes)
    store = createStore()
    searchForm = mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Shows the buy and sell FAQ', async() => {
    await router.push('/faq/buying-and-selling/')
    wrapper = mount(BuyAndSell, {localVue, router, store, sync: false, attachToDocument: true})
    const vm = wrapper.vm as any
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.params).toEqual({question: 'how-to-buy'})
    setPricing(store, localVue)
    await vm.$nextTick()
  })
  it('Sends the user to search', async() => {
    searchForm.fields.q.update('stuff', false)
    await router.push('/faq/buying-and-selling/')
    wrapper = mount(BuyAndSell, {localVue, router, store, sync: false, attachToDocument: true})
    const vm = wrapper.vm as any
    await wrapper.vm.$nextTick()
    wrapper.find('.who-is-open-link').trigger('click')
    await vm.$nextTick()
    expect(router.currentRoute.name).toBe('SearchProducts')
    expect(searchForm.fields.q.model).toBe('')
  })
})
