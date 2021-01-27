import Vue from 'vue'
import {cleanUp, createVuetify, docTarget, setViewer, vueSetup, mount} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import {genGuest, genOrder, genUser} from '@/specs/helpers/fixtures'
import Vuetify from 'vuetify/lib'
import AcOrderPreview from '@/components/AcOrderPreview.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {SingleController} from '@/store/singles/controller'
import Order from '@/types/Order'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let vuetify: Vuetify
let order: SingleController<Order>

describe('AcOrderPreview.ts', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    setViewer(store, genUser())
    order = mount(Empty, {localVue, store}).vm.$getSingle('order', {endpoint: '#', x: genOrder()})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Identifies whether the user is the buyer', async() => {
    wrapper = mount(
      AcOrderPreview, {
        localVue,
        store,
        vuetify,
        stubs: ['router-link'],
        propsData: {order, username: 'Fox', type: 'Sale'},

        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    expect(vm.isBuyer).toBe(true)
    setViewer(store, genUser({username: 'Vulpes'}))
    await vm.$nextTick()
    expect(vm.isBuyer).toBe(false)
  })
})
