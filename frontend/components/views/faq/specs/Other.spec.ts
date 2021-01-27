import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Router from 'vue-router'
import {faqRoutes} from './helpers'
import {Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import Other from '@/components/views/faq/Other.vue'
import {cleanUp, createVuetify, docTarget, vueSetup, mount} from '@/specs/helpers'

const localVue = vueSetup()
localVue.use(Router)

describe('Other.vue', () => {
  let router: Router
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  let vuetify: Vuetify
  beforeEach(() => {
    router = new Router(faqRoutes)
    vuetify = createVuetify()
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('mounts', async() => {
    await router.push('/faq/other/')
    wrapper = mount(Other, {localVue, router, store, vuetify, attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.params).toEqual({question: 'content-ratings'})
  })
})
