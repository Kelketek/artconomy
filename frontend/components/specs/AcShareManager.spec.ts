import {cleanUp, createVuetify, docTarget, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import AcShareManager from '@/components/AcShareManager.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {Vuetify} from 'vuetify'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let vuetify: Vuetify

describe('AcShareManager.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    const list = mount(Empty, {localVue, store}).vm.$getList('stuff', {endpoint: '/'})
    wrapper = mount(AcShareManager, {
      localVue,
      store,
      vuetify,
      propsData: {controller: list},

      attachTo: docTarget(),
      stubs: ['ac-bound-field'],
    })
  })
})
