import {genDeliverable, genUser} from '@/specs/helpers/fixtures'
import {cleanUp, confirmAction, createVuetify, docTarget, flushPromises, rs, setViewer, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import DeliverablePayment from '@/components/views/order/deliverable/DeliverablePayment.vue'
import {DeliverableStatus} from '@/types/DeliverableStatus'
import {dummyLineItems} from '@/lib/specs/helpers'
import mockAxios from '@/__mocks__/axios'
import {LineTypes} from '@/types/LineTypes'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import Vue from 'vue'
import {Vuetify} from 'vuetify'
import {deliverableRouter} from '@/components/views/order/specs/helpers'
import {SingleController} from '@/store/singles/controller'
import LineItem from '@/types/LineItem'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('DeliverablePayment.vue', () => {
  beforeEach(() => {
    jest.useFakeTimers()
    store = createStore()
    vuetify = createVuetify()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Updates after payment', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5/payment')
    wrapper = mount(
      DeliverablePayment, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox'},

        attachTo: docTarget(),
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    deliverable.order.seller.landscape = true
    deliverable.order.buyer!.landscape = false
    deliverable.status = DeliverableStatus.PAYMENT_PENDING
    vm.deliverable.makeReady(deliverable)
    vm.revisions.ready = true
    vm.characters.setList([])
    vm.characters.fetching = false
    vm.characters.ready = false
    vm.order.makeReady(deliverable.order)
    vm.lineItems.setList(dummyLineItems())
    mockAxios.reset()
    await vm.$nextTick()
    vm.lineItems.ready = true
    vm.lineItems.fetching = false
    await vm.$nextTick()
    wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    const paymentRequest = mockAxios.lastReqGet()
    expect(paymentRequest.url).toBe('/api/sales/v1/order/1/deliverables/5/pay/')
    mockAxios.mockResponse(rs({...deliverable, status: DeliverableStatus.QUEUED}), paymentRequest)
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(vm.deliverable.x.status).toBe(DeliverableStatus.QUEUED)
  })
  it('Permits tipping', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5/payment')
    wrapper = mount(
      DeliverablePayment, {
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
    deliverable.order.seller.landscape = true
    deliverable.order.buyer!.landscape = false
    deliverable.status = DeliverableStatus.PAYMENT_PENDING
    vm.deliverable.makeReady(deliverable)
    vm.revisions.ready = true
    vm.characters.setList([])
    vm.characters.fetching = false
    vm.characters.ready = false
    vm.order.makeReady(deliverable.order)
    vm.lineItems.setList(dummyLineItems())
    mockAxios.reset()
    await vm.$nextTick()
    vm.lineItems.ready = true
    vm.lineItems.fetching = false
    await vm.$nextTick()
    wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    wrapper.find('.preset10').trigger('click')
    await vm.$nextTick()
    expect(mockAxios.lastReqGet().data).toEqual({
      amount: '8.00',
      percentage: 0,
      type: LineTypes.TIP,
    })
  })
  it('Sends a status update', async() => {
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    setViewer(store, vulpes)
    router.push('/sales/Vulpes/sale/1/deliverables/5/payment')
    wrapper = mount(
      DeliverablePayment, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Sale', username: 'Vulpes'},

        attachTo: docTarget(),
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    deliverable.order.seller.landscape = true
    deliverable.order.buyer!.landscape = false
    deliverable.status = DeliverableStatus.NEW
    vm.deliverable.makeReady(deliverable)
    vm.revisions.ready = true
    vm.characters.setList([])
    vm.characters.fetching = false
    vm.characters.ready = false
    vm.order.makeReady(deliverable.order)
    vm.lineItems.setList(dummyLineItems())
    mockAxios.reset()
    await vm.$nextTick()
    vm.lineItems.ready = true
    vm.lineItems.fetching = false
    mockAxios.reset()
    await vm.$nextTick()
    await confirmAction(wrapper, ['.accept-order'])
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest.url).toBe('/api/sales/v1/order/1/deliverables/5/accept/')
    const newDeliverable = {...deliverable, ...{status: 2}}
    mockAxios.mockResponse(rs(newDeliverable), lastRequest)
    await flushPromises()
    await vm.$nextTick()
    expect(vm.deliverable.x.status).toBe(2)
  })
  it('Identifies seller and buyer outputs', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5/payment')
    wrapper = mount(
      DeliverablePayment, {
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
    vm.deliverable.setX(deliverable)
    await vm.$nextTick()
    expect(vm.buyerSubmission).toBeNull()
    expect(vm.sellerSubmission).toBeNull()
    const buyerSubmission = genSubmission()
    buyerSubmission.id = 398
    buyerSubmission.owner.username = 'Fox'
    vm.outputs.uniquePush(buyerSubmission)
    await vm.$nextTick()
    expect(vm.buyerSubmission.x.id).toBe(398)
    expect(vm.sellerSubmission).toBeNull()
    const sellerSubmission = genSubmission()
    sellerSubmission.id = 409
    sellerSubmission.owner.username = 'Vulpes'
    vm.outputs.uniquePush(sellerSubmission)
    expect(vm.buyerSubmission.x.id).toBe(398)
    expect(vm.sellerSubmission.x.id).toBe(409)
  })
  it('Clears the remote ID and cash flag when the manual transaction menu is toggled', async() => {
    const fox = genUser({is_staff: true})
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverablePayment, {
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
    vm.deliverable.setX(deliverable)
    vm.deliverable.ready = true
    mockAxios.reset()
    await vm.$nextTick()
    vm.paymentForm.fields.cash.update(true)
    vm.paymentForm.fields.remote_id.update('1234')
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.value).toBe(true)
    expect(vm.paymentForm.fields.remote_id.value).toBe('1234')
    vm.showManualTransaction = true
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.value).toBe(false)
    expect(vm.paymentForm.fields.remote_id.value).toBe('')
    vm.paymentForm.fields.cash.update(true)
    vm.paymentForm.fields.remote_id.update('1234')
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.value).toBe(true)
    expect(vm.paymentForm.fields.remote_id.value).toBe('1234')
    vm.showManualTransaction = false
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.value).toBe(false)
    expect(vm.paymentForm.fields.remote_id.value).toBe('')
  })
  it('Generates tip line item', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverablePayment, {
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
    vm.deliverable.setX(deliverable)
    vm.deliverable.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    vm.lineItems.setList(dummyLineItems())
    vm.setTip(0.25)
    const lastReq = mockAxios.lastReqGet()
    expect(lastReq.url).toEqual('/api/sales/v1/order/1/deliverables/5/line-items/')
    expect(lastReq.method).toEqual('post')
    expect(lastReq.data).toEqual({
      amount: '20.00',
      percentage: 0,
      type: LineTypes.TIP,
    })
    const tipLine = {
      amount: 5,
      percentage: 0,
      type: LineTypes.TIP,
      priority: 200,
      cascade_percentage: false,
      cascade_amount: false,
    }
    mockAxios.mockResponse(rs({
      amount: 5,
      percentage: 0,
      type: LineTypes.TIP,
      priority: 200,
      cascade_percentage: false,
      cascade_amount: false,
    }))
    await flushPromises()
    expect(vm.lineItems.list.map((x: SingleController<LineItem>) => x.x)).toContainEqual(tipLine)
  })
  it('Updates an existing tip line item', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverablePayment, {
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
    vm.deliverable.setX(deliverable)
    vm.deliverable.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    const lines = dummyLineItems()
    lines.push({
      id: -20,
      amount: 5,
      percentage: 0,
      type: LineTypes.TIP,
      priority: 200,
      cascade_percentage: false,
      cascade_amount: false,
      back_into_percentage: false,
      description: '',
    })
    vm.lineItems.setList(lines)
    vm.setTip(0.25)
    await vm.$nextTick()
    expect(vm.tip).toBeTruthy()
    expect(vm.tip.patchers.amount.model).toBe('20.00')
  })
})
