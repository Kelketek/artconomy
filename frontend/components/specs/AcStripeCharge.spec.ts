import {cleanUp, createVuetify, mockCardMount, mount, vueSetup} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import AcStripeCharge from '@/components/AcStripeCharge.vue'
import {ArtStore, createStore} from '@/store'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let vuetify: Vuetify

describe('AcStripeCharge.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts and preps', async() => {
    wrapper = mount(AcStripeCharge, {localVue, store, vuetify})
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.card.mount).toBe(mockCardMount)
  })
})
