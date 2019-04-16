import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import Router from 'vue-router'
import {faqRoutes} from './helpers'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import {Singles} from '@/store/singles/registry'
import {ArtStore, createStore} from '@/store'
import {Lists} from '@/store/lists/registry'
import {Profiles} from '@/store/profiles/registry'
import About from '@/components/views/faq/About.vue'
import Other from '@/components/views/faq/Other.vue'

Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Router)
localVue.use(Vuex)
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)

describe('About.vue', () => {
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
    router.push('/faq/other/')
    wrapper = mount(Other, {localVue, router, store, sync: false, attachToDocument: true})
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.params).toEqual({question: 'content-ratings'})
  })
})
