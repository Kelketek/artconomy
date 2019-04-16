import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import Router from 'vue-router'
import FAQ from '@/components/views/faq/FAQ.vue'
import {faqRoutes} from './helpers'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import {Singles} from '@/store/singles/registry'
import {ArtStore, createStore} from '@/store'
import {Lists} from '@/store/lists/registry'
import {Profiles} from '@/store/profiles/registry'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Router)
localVue.use(Vuex)
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)

describe('FAQ.vue', () => {
  let router: Router
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  beforeEach(() => {
    router = new Router(faqRoutes)
    store = createStore()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('mounts', async() => {
    router.push('/faq/')
    wrapper = mount(FAQ, {localVue, router, store, sync: false, attachToDocument: true})
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.name).toEqual('About')
  })
})
