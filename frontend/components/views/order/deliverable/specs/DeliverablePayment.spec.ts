import {genDeliverable, genUser} from '@/specs/helpers/fixtures'
import {
  cleanUp,
  confirmAction,
  createVuetify,
  docTarget,
  flushPromises,
  mount,
  rs,
  setViewer,
  vueSetup,
} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import DeliverablePayment from '@/components/views/order/deliverable/DeliverablePayment.vue'
import {DeliverableStatus} from '@/types/DeliverableStatus'
import {dummyLineItems} from '@/lib/specs/helpers'
import mockAxios from '@/__mocks__/axios'
import MockDate from 'mockdate'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import Vue, {VueConstructor} from 'vue'
import Vuetify from 'vuetify/lib'
import {deliverableRouter} from '@/components/views/order/specs/helpers'
import {ConnectionStatus} from '@/types/ConnectionStatus'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {PROCESSORS} from '@/types/PROCESSORS'
import {parseISO} from '@/lib/lib'
import Deliverable from '@/types/Deliverable'

let localVue: VueConstructor
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('DeliverablePayment.vue', () => {
  beforeEach(() => {
    localVue = vueSetup()
    localVue.use(Router)
    jest.useFakeTimers()
    store = createStore()
    vuetify = createVuetify()
    router = deliverableRouter()
    // This is a saturday.
    MockDate.set(parseISO('2020-08-01'))
    mount(Empty, {store, localVue}).vm.$getSingle('socketState', {
      endpoint: '#',
      persist: true,
      x: {
        status: ConnectionStatus.CONNECTING,
        version: 'beep',
        serverVersion: '',
      },
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
    MockDate.reset()
  })
  it('Handles deletion', async() => {
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
    const deliverable = genDeliverable({processor: PROCESSORS.STRIPE})
    vm.deliverable.makeReady(deliverable)
    vm.revisions.makeReady([])
    vm.characters.makeReady([])
    vm.order.makeReady(deliverable.order)
    vm.lineItems.makeReady(dummyLineItems())
    mockAxios.reset()
    await vm.$nextTick()
    vm.lineItems.ready = true
    vm.lineItems.fetching = false
    await vm.$nextTick()
    vm.deliverable.markDeleted()
    await vm.$nextTick()
  })
  it('Gracefully handles commission info', async() => {
    const user = genUser()
    setViewer(store, user)
    router.push('/orders/Fox/order/1/deliverables/5/overview')
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
    expect(vm.commissionInfo).toBe('')
    const deliverable = genDeliverable()
    vm.order.makeReady(deliverable.order)
    deliverable.status = DeliverableStatus.PAYMENT_PENDING
    vm.deliverable.setX(deliverable)
    vm.deliverable.fetching = false
    vm.deliverable.ready = true
    await vm.$nextTick()
    vm.deliverable.updateX({commission_info: 'Stuff and things'})
    vm.sellerHandler.artistProfile.updateX({commission_info: 'This is a test'})
    await vm.$nextTick()
    expect(vm.commissionInfo).toBe('This is a test')
    vm.deliverable.updateX({status: DeliverableStatus.NEW})
    await vm.$nextTick()
    expect(vm.commissionInfo).toBe('This is a test')
    vm.deliverable.updateX({status: DeliverableStatus.QUEUED})
    await vm.$nextTick()
    expect(vm.commissionInfo).toBe('Stuff and things')
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
    expect(lastRequest.url).toBe('/api/sales/order/1/deliverables/5/accept/')
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
  it('Clears the cash flag when navigating off the cash tab', async() => {
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
    vm.cardTabs = 2
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.value).toBe(true)
    vm.cardTabs = 1
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.value).toBe(false)
  })
  it('Calculates the correct completion date.', async() => {
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
    expect(vm.deliveryDate).toBe(null)
    const deliverable = genDeliverable({
      expected_turnaround: 2, paid_on: null, adjustment_expected_turnaround: 1,
    })
    vm.deliverable.setX(deliverable)
    vm.deliverable.ready = true
    // August first is a saturday. Sunday, then two work days days, plus one more day for adjustment.
    expect(vm.deliveryDate).toEqual(parseISO('2020-08-06'))
    vm.deliverable.updateX({paid_on: parseISO('2020-06-01').toISOString()})
    await vm.$nextTick()
    expect(vm.deliveryDate).toEqual(parseISO('2020-06-05'))
  })
  it('Handles a Stripe Payment boop', async() => {
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
    const deliverable = genDeliverable({
      processor: PROCESSORS.STRIPE,
      status: DeliverableStatus.PAYMENT_PENDING,
    })
    vm.lineItems.makeReady(dummyLineItems())
    vm.deliverable.makeReady(deliverable)
    vm.revisions.makeReady([])
    vm.characters.makeReady([])
    vm.order.makeReady(deliverable.order)
    vm.clientSecret.makeReady({secret: 'beep'})
    await vm.$nextTick()
    wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(true)
    vm.$refs.cardManager.stripe().paymentValue = {}
    wrapper.find('.dialog-submit').trigger('click')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(false)
  })
  it('Handles a Stripe Payment with an existing card', async() => {
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
    const deliverable = genDeliverable({processor: PROCESSORS.STRIPE, status: DeliverableStatus.PAYMENT_PENDING})
    vm.lineItems.makeReady(dummyLineItems())
    vm.deliverable.makeReady(deliverable)
    vm.revisions.makeReady([])
    vm.characters.makeReady([])
    vm.order.makeReady(deliverable.order)
    vm.clientSecret.makeReady({secret: 'beep'})
    await vm.$nextTick()
    wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(true)
    vm.$refs.cardManager.stripe().paymentValue = {}
    vm.$refs.cardManager.tab = 'saved-cards'
    vm.paymentForm.fields.card_id.update(15)
    await vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(false)
  })
  it('Handles a Stripe Payment Failure', async() => {
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
    const deliverable = genDeliverable({processor: PROCESSORS.STRIPE, status: DeliverableStatus.PAYMENT_PENDING})
    vm.lineItems.makeReady(dummyLineItems())
    vm.deliverable.makeReady(deliverable)
    vm.revisions.makeReady([])
    vm.characters.makeReady([])
    vm.order.makeReady(deliverable.order)
    vm.clientSecret.makeReady({secret: 'beep'})
    await vm.$nextTick()
    wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(true)
    vm.$refs.cardManager.stripe().paymentValue = {
      error: {code: 'Failure', message: 'Shit broke.'},
    }
    wrapper.find('.dialog-submit').trigger('click')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(true)
    expect(vm.paymentForm.errors).toEqual(['Shit broke.'])
    vm.$refs.cardManager.stripe().paymentValue = {
      error: {code: 'Failure'},
    }
    wrapper.find('.dialog-submit').trigger('click')
    expect(vm.viewSettings.model.showPayment).toBe(true)
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.paymentForm.errors).toEqual(['An unknown error occurred while trying to reach Stripe. Please contact support.'])
  })
  const testTrippedForm = async(vm: any) => {
    vm.debouncedUpdateIntent.flush()
    await vm.$nextTick()
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest).toBeTruthy()
    expect(vm.paymentForm.sending).toBe(true)
    mockAxios.mockResponse(rs({secret: 'burp'}))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.paymentForm.sending).toBe(false)
    await flushPromises()
    mockAxios.reset()
    await vm.$nextTick()
  }
  it('Refetches the secret when the card settings are toggled', async() => {
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
    const deliverable = genDeliverable({processor: PROCESSORS.STRIPE, status: DeliverableStatus.PAYMENT_PENDING})
    vm.lineItems.makeReady(dummyLineItems())
    vm.deliverable.makeReady(deliverable)
    vm.revisions.makeReady([])
    vm.characters.makeReady([])
    vm.order.makeReady(deliverable.order)
    vm.clientSecret.makeReady({secret: 'beep'})
    await flushPromises()
    mockAxios.reset()
    await vm.$nextTick()
    vm.paymentForm.fields.make_primary.update(!vm.paymentForm.fields.make_primary.value)
    await testTrippedForm(vm)
    vm.paymentForm.fields.save_card.update(!vm.paymentForm.fields.save_card.value)
    await testTrippedForm(vm)
    vm.paymentForm.fields.card_id.update(555)
    await testTrippedForm(vm)
  })
  it('Calculates the total expected turnaround days', async() => {
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
    const deliverable = genDeliverable({
      processor: PROCESSORS.STRIPE,
      status: DeliverableStatus.QUEUED,
      expected_turnaround: 2,
      adjustment_expected_turnaround: 3,
    })
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.expectedTurnaround).toBe(5)
  })
  it('Calculates the total expected revisions', async() => {
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
    const deliverable = genDeliverable({
      processor: PROCESSORS.STRIPE,
      status: DeliverableStatus.QUEUED,
      revisions: 2,
      adjustment_revisions: 3,
    })
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.revisionCount).toBe(5)
  })
})

describe('DeliverablePayment.vue payment modal checks', () => {
  let vm: any
  let deliverable: Deliverable
  beforeEach(() => {
    localVue = vueSetup()
    localVue.use(Router)
    jest.useFakeTimers()
    store = createStore()
    vuetify = createVuetify()
    router = deliverableRouter()
    // This is a saturday.
    MockDate.set(parseISO('2020-08-01'))
    mount(Empty, {store, localVue}).vm.$getSingle('socketState', {
      endpoint: '#',
      persist: true,
      x: {
        status: ConnectionStatus.CONNECTING,
        version: 'beep',
        serverVersion: '',
      },
    })
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
    vm = wrapper.vm
    deliverable = genDeliverable({
      processor: PROCESSORS.STRIPE,
      status: DeliverableStatus.PAYMENT_PENDING,
    })
    vm.lineItems.makeReady(dummyLineItems())
    vm.deliverable.makeReady(deliverable)
    vm.revisions.makeReady([])
    vm.characters.makeReady([])
    vm.order.makeReady(deliverable.order)
    vm.clientSecret.makeReady({secret: 'beep'})
  })
  afterEach(() => {
    jest.clearAllTimers()
    cleanUp(wrapper)
    MockDate.reset()
  })
  it('Switches to and from cash mode', async() => {
    expect(vm.paymentForm.fields.cash.model).toBe(false)
    vm.cardTabs = 2
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.model).toBe(true)
    vm.cardTabs = 0
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.model).toBe(false)
  })
  it('Sets a default reader', async() => {
    expect(vm.cardTabs).toBe(0)
    vm.viewerHandler.user.updateX({is_staff: true})
    expect(vm.paymentForm.fields.use_reader.model).toBe(false)
    vm.readers.makeReady([{id: 'Test', name: 'Test Reader'}])
    await vm.$nextTick()
    // Should auto-switch.
    expect(vm.cardTabs).toBe(1)
    expect(vm.paymentForm.fields.use_reader.model).toBe(true)
    expect(vm.readerForm.fields.reader.model).toBe('Test')
    await vm.$nextTick()
  })
  it('Handles an empty reader list', async() => {
    expect(vm.cardTabs).toBe(0)
    vm.viewerHandler.user.updateX({is_staff: true})
    expect(vm.paymentForm.fields.use_reader.model).toBe(false)
    vm.cardTabs = 1
    await vm.$nextTick()
    expect(vm.paymentForm.fields.use_reader.model).toBe(true)
    expect(vm.readerForm.fields.reader.model).toBe(null)
    await vm.$nextTick()
  })
  it('Handles switching to manual key-in', async() => {
    expect(vm.cardTabs).toBe(0)
    vm.viewerHandler.user.updateX({is_staff: true})
    expect(vm.paymentForm.fields.use_reader.model).toBe(false)
    vm.readers.makeReady([{id: 'Test', name: 'Test Reader'}])
    await vm.$nextTick()
    // should auto-switch
    expect(vm.cardTabs).toBe(1)
    vm.cardTabs = 0
    await vm.$nextTick()
    expect(vm.paymentForm.fields.use_reader.model).toBe(false)
    // Should not remove the readerForm value.
    expect(vm.readerForm.fields.reader.model).toBe('Test')
    await vm.$nextTick()
  })
  it('Handles switching from staff to non-staff', async() => {
    expect(vm.cardTabs).toBe(0)
    vm.viewerHandler.user.updateX({is_staff: true})
    expect(vm.paymentForm.fields.use_reader.model).toBe(false)
    vm.readers.makeReady([{id: 'Test', name: 'Test Reader'}])
    await vm.$nextTick()
    // should auto-switch
    expect(vm.cardTabs).toBe(1)
    vm.viewerHandler.user.updateX({is_staff: false})
    await vm.$nextTick()
    expect(vm.cardTabs).toBe(0)
  })
  it('Hides the payment form after marking a deliverable as paid by cash', async() => {
    vm.viewerHandler.user.updateX({is_staff: true})
    vm.cardTabs = 2
    await vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    expect(vm.viewSettings.patchers.showPayment.model).toBe(true)
    wrapper.find('.mark-paid-cash').trigger('click')
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest.url).toBe(
      `/api/sales/invoice/${deliverable.invoice}/pay/`,
    )
    mockAxios.mockResponse(rs(deliverable))
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.viewSettings.patchers.showPayment.model).toBe(false)
  })
})
