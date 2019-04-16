import Vue from 'vue'
import {vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import AcOrderRating from '@/components/views/order/AcOrderRating.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcOrderRating.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts', async() => {
    wrapper = mount(AcOrderRating, {
      localVue, store, propsData: {orderId: 3, end: 'buyer'}, sync: false, attachToDocument: true,
    })
  })
})
