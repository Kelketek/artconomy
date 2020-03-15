import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
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
      sync: false,
      attachToDocument: true,
    })
  })
})
