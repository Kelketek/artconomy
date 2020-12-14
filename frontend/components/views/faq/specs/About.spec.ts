import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Router from 'vue-router'
import {faqRoutes} from './helpers'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import About from '@/components/views/faq/About.vue'
import {cleanUp, createVuetify, docTarget, vueSetup} from '@/specs/helpers'

const localVue = vueSetup()
localVue.use(Router)

describe('About.vue', () => {
  let router: Router
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  let vuetify: Vuetify
  beforeEach(() => {
    router = new Router(faqRoutes)
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('mounts', async() => {
    await router.push('/faq/about/')
    wrapper = mount(About, {localVue, router, store, vuetify, attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.params).toEqual({question: 'what-is-artconomy'})
  })
  it('sets a question', async() => {
    await router.push('/faq/about/what-is-artconomy/')
    wrapper = mount(About, {localVue, router, store, vuetify, attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    const header = wrapper.findAll('.v-expansion-panel-header').at(1)
    header.trigger('click')
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.params).toEqual({question: 'cost'})
  })
})
