import Vue from 'vue'
import Router from 'vue-router'
import FAQ from '@/components/views/faq/FAQ.vue'
import {faqRoutes} from './helpers'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, vueSetup} from '@/specs/helpers'
import {Vuetify} from 'vuetify/types'

const localVue = vueSetup()
localVue.use(Router)

describe('FAQ.vue', () => {
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
    router.push('/faq/')
    wrapper = mount(FAQ, {localVue, router, store, vuetify, attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.name).toEqual('About')
  })
})
