import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {cleanUp, createVuetify, docTarget, vueSetup, mount} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import AcDeliverableRating from '@/components/views/order/AcDeliverableRating.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcDeliverableRating.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    wrapper = mount(AcDeliverableRating, {
      localVue,
      store,
      vuetify,
      propsData: {orderId: 3, end: 'buyer', deliverableId: 5},

      attachTo: docTarget(),
    })
  })
})
