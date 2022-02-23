import {cleanUp, createVuetify, docTarget, flushPromises, rs, setViewer, vueSetup, mount} from '@/specs/helpers'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {deliverableRouter} from '@/components/views/order/specs/helpers'
import {genDeliverable, genUser} from '@/specs/helpers/fixtures'
import DeliverableOverview from '@/components/views/order/deliverable/DeliverableOverview.vue'
import mockAxios from '@/__mocks__/axios'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('DeliverableOverview.vue', () => {
  beforeEach(() => {
    jest.useFakeTimers()
    store = createStore()
    vuetify = createVuetify()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Handles a null product', async() => {
    const user = genUser()
    setViewer(store, user)
    router.push('/orders/Fox/order/1/deliverables/5/overview')
    wrapper = mount(
      DeliverableOverview, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox'},
        attachTo: docTarget(),
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    deliverable.product = null
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.name).toBe('(Custom Project)')
  })
  it('Sends an invite email', async() => {
    const user = genUser()
    setViewer(store, user)
    router.push('/orders/Fox/order/1/deliverables/5/overview')
    wrapper = mount(
      DeliverableOverview, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox'},
        attachTo: docTarget(),
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    deliverable.order.buyer = null
    deliverable.order.seller = user
    deliverable.order.customer_email = 'stuff@example.com'
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.send-invite-button').trigger('click')
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest.url).toBe('/api/sales/v1/order/1/deliverables/5/invite/')
    mockAxios.mockResponse(rs(deliverable.order))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.inviteSent).toBe(true)
  })
  it('Loads with the order confirmation triggered', async() => {
    setViewer(store, genUser())
    router.push('/orders/Fox/order/1/deliverables/5/overview?showConfirm=true')
    wrapper = mount(
      DeliverableOverview, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox'},
        attachTo: docTarget(),
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.showConfirm).toBe(true)
  })
})
