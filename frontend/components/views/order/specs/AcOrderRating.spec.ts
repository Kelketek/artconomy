import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import AcOrderRating from '@/components/views/order/AcOrderRating.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcOrderRating.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    wrapper = mount(AcOrderRating, {
      localVue,
      store,
      vuetify,
      propsData: {orderId: 3, end: 'buyer'},
      sync: false,
      attachToDocument: true,
    })
  })
})
