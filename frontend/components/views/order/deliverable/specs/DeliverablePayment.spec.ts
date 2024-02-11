import {genDeliverable, genUser} from '@/specs/helpers/fixtures.ts'
import {
  cleanUp,
  confirmAction,
  docTarget,
  flushPromises,
  mount,
  rs,
  setViewer,
  vueSetup,
  VuetifyWrapped,
} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import DeliverablePayment from '@/components/views/order/deliverable/DeliverablePayment.vue'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import {dummyLineItems} from '@/lib/specs/helpers.ts'
import mockAxios from '@/__mocks__/axios.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import {Router} from 'vue-router'
import {ArtStore, createStore} from '@/store/index.ts'
import {deliverableRouter} from '@/components/views/order/specs/helpers.ts'
import {ConnectionStatus} from '@/types/ConnectionStatus.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {PROCESSORS} from '@/types/PROCESSORS.ts'
import {parseISO} from '@/lib/lib.ts'
import Deliverable from '@/types/Deliverable.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

const WrappedDeliverablePayment = VuetifyWrapped(DeliverablePayment)

describe('DeliverablePayment.vue', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
    // This is a saturday.
    vi.setSystemTime(parseISO('2020-08-01'))
    mount(Empty, vueSetup({store})).vm.$getSingle('socketState', {
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
  })
  test('Handles deletion', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/payment')
    wrapper = mount(
      DeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
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
  test('Gracefully handles commission info', async() => {
    const user = genUser()
    setViewer(store, user)
    router.push('/orders/Fox/order/1/deliverables/5/overview')
    wrapper = mount(
      DeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
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
  test('Sends a status update', async() => {
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    setViewer(store, vulpes)
    await router.push('/sales/Vulpes/sale/1/deliverables/5/payment')
    wrapper = mount(
      WrappedDeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Sale',
          username: 'Vulpes',
        },
      })
    const vm = wrapper.vm.$refs.vm as any
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
  test('Identifies seller and buyer outputs', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/payment')
    wrapper = mount(
      DeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
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
    expect(vm.buyerSubmission.id).toBe(398)
    expect(vm.sellerSubmission).toBeNull()
    const sellerSubmission = genSubmission()
    sellerSubmission.id = 409
    sellerSubmission.owner.username = 'Vulpes'
    vm.outputs.uniquePush(sellerSubmission)
    expect(vm.buyerSubmission.id).toBe(398)
    expect(vm.sellerSubmission.id).toBe(409)
  })
  test('Clears the cash flag when navigating off the cash tab', async() => {
    const fox = genUser({is_staff: true})
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
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
  test('Calculates the correct completion date.', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const vm = wrapper.vm as any
    expect(vm.deliveryDate).toBe(null)
    const deliverable = genDeliverable({
      expected_turnaround: 2,
      paid_on: null,
      adjustment_expected_turnaround: 1,
    })
    vm.deliverable.setX(deliverable)
    vm.deliverable.ready = true
    // August first is a saturday. Sunday, then two work days days, plus one more day for adjustment.
    expect(vm.deliveryDate).toEqual(parseISO('2020-08-06'))
    vm.deliverable.updateX({paid_on: parseISO('2020-06-01').toISOString()})
    await vm.$nextTick()
    expect(vm.deliveryDate).toEqual(parseISO('2020-06-05'))
  })
  test('Handles a Stripe Payment boop', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const vm = wrapper.vm.$refs.vm as any
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
    await wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(true)
    vm.$refs.cardManager.stripe().paymentValue = {}
    await wrapper.find('.dialog-submit').trigger('click')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(false)
  })
  test('Handles a Stripe Payment with an existing card', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const vm = wrapper.vm.$refs.vm as any
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
    await wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(true)
    vm.$refs.cardManager.stripe().paymentValue = {}
    vm.$refs.cardManager.tab = 'saved-cards'
    vm.paymentForm.fields.card_id.update(15)
    await vm.$nextTick()
    await wrapper.find('.dialog-submit').trigger('click')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(false)
  })
  test('Handles a Stripe Payment Failure', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const vm = wrapper.vm.$refs.vm as any
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
    await wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(true)
    vm.$refs.cardManager.stripe().paymentValue = {
      error: {
        code: 'Failure',
        message: 'Shit broke.',
      },
    }
    await wrapper.find('.dialog-submit').trigger('click')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(vm.viewSettings.model.showPayment).toBe(true)
    expect(vm.paymentForm.errors).toEqual(['Shit broke.'])
    vm.$refs.cardManager.stripe().paymentValue = {
      error: {code: 'Failure'},
    }
    await wrapper.find('.dialog-submit').trigger('click')
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
  test('Refetches the secret when the card settings are toggled', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
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
    await flushPromises()
    mockAxios.reset()
    await vm.$nextTick()
    vm.paymentForm.fields.make_primary.update(!vm.paymentForm.fields.make_primary.value)
    await testTrippedForm(vm)
    vm.paymentForm.fields.save_card.update(!vm.paymentForm.fields.save_card.value)
    await testTrippedForm(vm)
    vm.paymentForm.fields.card_id.update(555)
    await testTrippedForm(vm)
  }, 10000)
  test('Calculates the total expected turnaround days', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
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
  test('Calculates the total expected revisions', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverablePayment, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
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
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
    // This is a saturday.
    vi.setSystemTime(parseISO('2020-08-01'))
    const options = vueSetup({
      store,
      extraPlugins: [router],
      stubs: ['ac-revision-manager'],
    })
    mount(Empty, vueSetup({
      store,
      stubs: ['ac-revision-manager'],
    })).vm.$getSingle('socketState', {
      endpoint: '#',
      persist: true,
      x: {
        status: ConnectionStatus.CONNECTING,
        version: 'beep',
        serverVersion: '',
      },
    })
    wrapper = mount(
      WrappedDeliverablePayment, {
        ...options,
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
        attachTo: docTarget(),
      })
    vm = wrapper.vm.$refs.vm
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
    vi.clearAllTimers()
    cleanUp(wrapper)
  })
  test('Switches to and from cash mode', async() => {
    expect(vm.paymentForm.fields.cash.model).toBe(false)
    vm.cardTabs = 2
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.model).toBe(true)
    vm.cardTabs = 0
    await vm.$nextTick()
    expect(vm.paymentForm.fields.cash.model).toBe(false)
  })
  test('Sets a default reader', async() => {
    expect(vm.cardTabs).toBe(0)
    vm.viewerHandler.user.updateX({is_staff: true})
    expect(vm.paymentForm.fields.use_reader.model).toBe(false)
    vm.readers.makeReady([{
      id: 'Test',
      name: 'Test Reader',
    }])
    await vm.$nextTick()
    // Should auto-switch.
    expect(vm.cardTabs).toBe(1)
    expect(vm.paymentForm.fields.use_reader.model).toBe(true)
    expect(vm.readerForm.fields.reader.model).toBe('Test')
    await vm.$nextTick()
  })
  test('Handles an empty reader list', async() => {
    expect(vm.cardTabs).toBe(0)
    vm.viewerHandler.user.updateX({is_staff: true})
    expect(vm.paymentForm.fields.use_reader.model).toBe(false)
    vm.cardTabs = 1
    await vm.$nextTick()
    expect(vm.paymentForm.fields.use_reader.model).toBe(true)
    expect(vm.readerForm.fields.reader.model).toBe(null)
    await vm.$nextTick()
  })
  test('Handles switching to manual key-in', async() => {
    expect(vm.cardTabs).toBe(0)
    vm.viewerHandler.user.updateX({is_staff: true})
    expect(vm.paymentForm.fields.use_reader.model).toBe(false)
    vm.readers.makeReady([{
      id: 'Test',
      name: 'Test Reader',
    }])
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
  test('Handles switching from staff to non-staff', async() => {
    expect(vm.cardTabs).toBe(0)
    vm.viewerHandler.user.updateX({is_staff: true})
    expect(vm.paymentForm.fields.use_reader.model).toBe(false)
    vm.readers.makeReady([{
      id: 'Test',
      name: 'Test Reader',
    }])
    await vm.$nextTick()
    // should auto-switch
    expect(vm.cardTabs).toBe(1)
    vm.viewerHandler.user.updateX({is_staff: false})
    await vm.$nextTick()
    expect(vm.cardTabs).toBe(0)
  })
  test('Hides the payment form after marking a deliverable as paid by cash', async() => {
    vm.viewerHandler.user.updateX({is_staff: true})
    vm.cardTabs = 2
    await vm.$nextTick()
    mockAxios.reset()
    await wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    expect(vm.viewSettings.patchers.showPayment.model).toBe(true)
    await wrapper.find('.mark-paid-cash').trigger('click')
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
