import {genDeliverable, genRevision, genUser} from '@/specs/helpers/fixtures'
import {cleanUp, createVuetify, docTarget, flushPromises, rs, setViewer, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {deliverableRouter} from '@/components/views/order/specs/helpers'
import DeliverableRevisions from '@/components/views/order/deliverable/DeliverableRevisions.vue'
import {DeliverableStatus} from '@/types/DeliverableStatus'
import mockAxios from '@/__mocks__/axios'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('DeliverableRevisions.vue', () => {
  beforeEach(() => {
    jest.useFakeTimers()
    store = createStore()
    vuetify = createVuetify()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Determines the final', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5/revisions')
    wrapper = mount(
      DeliverableRevisions, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox'},

        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    vm.revisions.setList([genRevision()])
    vm.revisions.ready = true
    vm.revisions.fetching = false
    expect(vm.final).toBeFalsy()
    vm.deliverable.updateX({final_uploaded: true})
    expect(vm.final).toBeTruthy()
  })
  it('Refreshes the deliverable when the list changes', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5/revisions')
    wrapper = mount(
      DeliverableRevisions, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox'},

        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    vm.revisions.setList([])
    vm.revisions.ready = true
    vm.revisions.fetching = false
    const spyRefresh = jest.spyOn(vm.deliverable, 'refresh')
    await vm.$nextTick()
    expect(spyRefresh).not.toHaveBeenCalled()
    vm.revisions.uniquePush(genRevision())
    await vm.$nextTick()
    expect(spyRefresh).toHaveBeenCalled()
  })
  it('Autosubmits when a new file is added', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5/revisions')
    wrapper = mount(
      DeliverableRevisions, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox'},

        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    const spySubmit = jest.spyOn(vm.newRevision, 'submitThen')
    const deliverable = genDeliverable()
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    vm.revisions.setList([])
    vm.revisions.ready = true
    vm.revisions.fetching = false
    mockAxios.reset()
    await vm.$nextTick()
    vm.newRevision.fields.file.update('Stuff')
    await vm.$nextTick()
    expect(spySubmit).toHaveBeenCalledWith(expect.any(Function))
    const req = mockAxios.lastReqGet()
    mockAxios.mockResponse(rs(genRevision()), req)
    await flushPromises()
    await vm.$nextTick()
    expect(vm.revisions.list.length).toBe(1)
  })
  it('Fetches revisions if they are newly permitted to be seen', async() => {
    setViewer(store, genUser())
    router.push('/orders/Fox/order/1/deliverables/5/revisions')
    wrapper = mount(
      DeliverableRevisions, {
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
    deliverable.status = DeliverableStatus.PAYMENT_PENDING
    deliverable.revisions_hidden = true
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    const mockGet = jest.spyOn(vm.revisions, 'get')
    vm.deliverable.updateX({revisions_hidden: false})
    await vm.$nextTick()
    expect(mockGet).toHaveBeenCalled()
  })
})
