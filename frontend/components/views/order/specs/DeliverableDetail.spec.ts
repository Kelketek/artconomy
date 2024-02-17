import {cleanUp, flushPromises, mount, rs, setViewer, vueSetup, VuetifyWrapped} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import DeliverableDetail from '@/components/views/order/DeliverableDetail.vue'
import {genArtistProfile, genDeliverable, genGuest, genReference, genUser} from '@/specs/helpers/fixtures.ts'
import mockAxios from '@/__mocks__/axios.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import {Router} from 'vue-router'
import {deliverableRouter} from '@/components/views/order/specs/helpers.ts'
import {VIEWER_TYPE} from '@/types/VIEWER_TYPE.ts'
import {genCharacter} from '@/store/characters/specs/fixtures.ts'
import {add, formatISO} from 'date-fns'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

const WrappedDeliverableDetail = VuetifyWrapped(DeliverableDetail)

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe('DeliverableDetail.vue', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Identifies seller, buyer, and arbitrator', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/')
    wrapper = mount(
      DeliverableDetail, {
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
    const arbitrator = genUser()
    arbitrator.username = 'Foxxo'
    deliverable.arbitrator = arbitrator
    const deliverableRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/')
    mockAxios.mockResponse(rs(deliverable), deliverableRequest)
    await flushPromises()
    await vm.$nextTick()
    expect(vm.buyer.username).toBe('Fox')
    expect(vm.seller.username).toBe('Vulpes')
    expect(vm.arbitrator.username).toBe('Foxxo')
    expect(vm.isArbitrator).toBe(false)
    vm.viewMode = VIEWER_TYPE.STAFF
    await vm.$nextTick()
    expect(vm.isArbitrator).toBe(true)
  })
  test('Scrolls to the bottom section', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/')
    wrapper = mount(
      DeliverableDetail, {
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
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    const spyGoTo = vi.spyOn(vm, '$goTo')
    await wrapper.find('.review-terms-button').trigger('click')
    await vm.$nextTick()
    expect(spyGoTo).toHaveBeenCalledWith('.section-scroll-target')
  })
  test('Handles a null buyer', async() => {
    const vulpes = genUser()
    vulpes.username = 'Fox'
    setViewer(store, vulpes)
    await router.push('/orders/Fox/order/1/deliverables/5/')
    wrapper = mount(
      DeliverableDetail, {
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
    deliverable.order.buyer = null
    const deliverableRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/')
    mockAxios.mockResponse(rs(deliverable), deliverableRequest)
    expect(vm.buyer).toBe(null)
    expect(vm.buyerSubmission).toBe(null)
    expect(vm.viewerItems).toEqual([
      {
        title: 'Please select...',
        value: VIEWER_TYPE.UNSET,
      },
      {
        title: 'Staff',
        value: VIEWER_TYPE.STAFF,
      },
      {
        title: 'Seller',
        value: VIEWER_TYPE.SELLER,
      },
    ])
  })
  test('Sends a seller to their new submission', async() => {
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    setViewer(store, vulpes)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverableDetail, {
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
    const deliverable = genDeliverable()
    deliverable.status = DeliverableStatus.COMPLETED
    vm.deliverable.setX(deliverable)
    vm.deliverable.fetching = false
    vm.deliverable.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.gallery-add').trigger('click')
    await vm.$nextTick()
    mockAxios.reset()
    await vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    const newSubmission = genSubmission()
    newSubmission.id = 101
    const newSubmissionRequest = mockAxios.lastReqGet()
    expect(newSubmissionRequest.url).toBe('/api/sales/order/1/deliverables/5/outputs/')
    mockAxios.mockResponse(rs(newSubmission))
    await flushPromises()
    await vm.$nextTick()
    expect(router.currentRoute.value.name).toBe('Submission')
    expect(router.currentRoute.value.params).toEqual({submissionId: '101'})
    expect(router.currentRoute.value.query).toEqual({editing: 'true'})
  })
  test('Handles an order without a product', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      WrappedDeliverableDetail, {
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
    const deliverable = genDeliverable()
    deliverable.product = null
    deliverable.status = DeliverableStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/')
    mockAxios.mockResponse(rs(deliverable), orderRequest)
    await flushPromises()
    await vm.$nextTick()
  })
  test('Handles different view modes', async() => {
    const user = genUser({is_staff: true})
    user.username = 'Dude'
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverableDetail, {
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
    const deliverable = genDeliverable()
    deliverable.product = null
    deliverable.status = DeliverableStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/')
    mockAxios.mockResponse(rs(deliverable), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    expect(wrapper.find('.view-mode-select').exists()).toBe(true)
    expect(vm.viewMode).toBe(0)
    expect(vm.isBuyer).toBe(false)
    expect(vm.isSeller).toBe(false)
    expect(vm.isBuyer).toBe(false)
    vm.viewMode = 1
    await vm.$nextTick()
    expect(vm.isBuyer).toBe(true)
    expect(vm.isSeller).toBe(false)
    expect(vm.isArbitrator).toBe(false)
    vm.viewMode = 2
    await vm.$nextTick()
    expect(vm.isBuyer).toBe(false)
    expect(vm.isSeller).toBe(true)
    expect(vm.isArbitrator).toBe(false)
    vm.viewMode = 3
    await vm.$nextTick()
    expect(vm.isBuyer).toBe(false)
    expect(vm.isSeller).toBe(false)
    expect(vm.isArbitrator).toBe(true)
  })
  test('Figures if non-completion time has elapsed', async() => {
    const user = genUser()
    user.username = 'Dude'
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverableDetail, {
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
    const deliverable = genDeliverable()
    deliverable.product = null
    deliverable.status = DeliverableStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/')
    mockAxios.mockResponse(rs(deliverable), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    // @ts-ignore
    vm.deliverable.updateX({dispute_available_on: formatISO(add(new Date(), {days: 7}))})
    await vm.$nextTick()
    // '2019-07-26T15:04:41.078424-05:00'
    expect(vm.disputeTimeElapsed).toBe(false)
    vm.deliverable.updateX({dispute_available_on: '2019-07-26T15:04:41.078424-05:00'})
    await vm.$nextTick()
    expect(vm.disputeTimeElapsed).toBe(true)
    vm.deliverable.updateX({dispute_available_on: null})
    await vm.$nextTick()
    expect(vm.disputeTimeElapsed).toBe(false)
  })
  test('Determines if the dispute window is open', async() => {
    const user = genUser()
    user.username = 'Dude'
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverableDetail, {
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
    const deliverable = genDeliverable()
    deliverable.product = null
    deliverable.trust_finalized = true
    deliverable.auto_finalize_on = formatISO(add(new Date(), {days: 7}))
    deliverable.status = DeliverableStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/')
    mockAxios.mockResponse(rs(deliverable), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    expect(vm.disputeWindow).toBe(true)
    vm.deliverable.updateX({auto_finalize_on: '2019-07-26T15:04:41.078424-05:00'})
    await vm.$nextTick()
    expect(vm.disputeWindow).toBe(false)
    vm.deliverable.updateX({auto_finalize_on: null})
    expect(vm.disputeWindow).toBe(false)
  })
  test('Prompts to add revision to collection', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverableDetail, {
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
    const deliverable = genDeliverable()
    deliverable.product = null
    deliverable.status = DeliverableStatus.COMPLETED
    deliverable.revisions_hidden = false
    vm.deliverable.setX(deliverable)
    vm.deliverable.ready = true
    vm.deliverable.fetching = false
    await vm.$nextTick()
    expect(vm.showAdd)
    wrapper.find('.collection-add').trigger('click')
    await vm.$nextTick()
    expect(vm.viewSettings.model.showAddSubmission).toBe(true)
  })
  test('Prompts to add revision to collection by registering if they are a guest', async() => {
    const user = genGuest()
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverableDetail, {
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
    const deliverable = genDeliverable()
    deliverable.order.buyer = {...user}
    deliverable.product = null
    deliverable.status = DeliverableStatus.COMPLETED
    deliverable.order.claim_token = 'sdvi397awr'
    deliverable.revisions_hidden = false
    vm.deliverable.setX(deliverable)
    vm.deliverable.ready = true
    vm.deliverable.fetching = false
    await vm.$nextTick()
    await wrapper.find('.collection-add').trigger('click')
    await vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toEqual(
      '/login/register/?claim=sdvi397awr&next=/orders/Fox/order/1/deliverables/5/?showAdd=true',
    )
  })
  test('Does not have the submission adding form loaded by default', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
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
    expect(vm.viewSettings.model.showAddSubmission).toBe(false)
  })
  test('Loads with the submission prompt triggered', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/deliverables/5?showAdd=true')
    wrapper = mount(
      DeliverableDetail, {
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
    expect(vm.viewSettings.model.showAddSubmission).toBe(true)
  })
  test('Prompts to link a guest account', async() => {
    const user = genGuest()
    user.username = '__1'
    setViewer(store, user)
    await router.push('/orders/__1/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: '__1',
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    deliverable.order.buyer = {...user}
    deliverable.order.claim_token = 'sdvi397awr'
    deliverable.revisions_hidden = false
    vm.deliverable.setX(deliverable)
    vm.deliverable.ready = true
    vm.deliverable.fetching = false
    await vm.$nextTick()
    await wrapper.find('.link-account').trigger('click')
    await vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toEqual(
      '/login/register/?claim=sdvi397awr&next=/orders/__1/order/1/deliverables/5/',
    )
  })
  test('Calculates the deliverable turnaround time', async() => {
    const user = genGuest()
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      WrappedDeliverableDetail, {
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
    const deliverable = genDeliverable()
    deliverable.order.buyer = {...user}
    deliverable.product = null
    deliverable.status = DeliverableStatus.COMPLETED
    deliverable.expected_turnaround = 3
    deliverable.order.claim_token = 'sdvi397awr'
    deliverable.revisions_hidden = false
    vm.deliverable.makeReady(deliverable)
    vm.order.makeReady(deliverable.order)
    await vm.$nextTick()
    expect(vm.expectedTurnaround).toBe(3)
  })
  test('Calculates revision time', async() => {
    const user = genGuest()
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
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
    deliverable.order.buyer = {...user}
    deliverable.product = null
    deliverable.revisions = 3
    vm.deliverable.makeReady(deliverable)
    vm.order.makeReady(deliverable.order)
    await vm.$nextTick()
    expect(vm.revisionCount).toBe(3)
  })
  test('Adds character tags to submission form', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
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
    vm.deliverable.setX(genDeliverable())
    vm.deliverable.fetching = false
    vm.deliverable.ready = true
    vm.fetching = false
    vm.revisions.setList([])
    vm.revisions.fetching = false
    vm.revisions.ready = true
    await vm.$nextTick()
    const characterRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/characters/')
    const character = genCharacter()
    character.tags = ['stuff', 'things', 'wat']
    mockAxios.mockResponse(rs([{
      id: 1,
      character,
    }]), characterRequest)
    await flushPromises()
    await vm.$nextTick()
    expect([...vm.addSubmission.fields.tags.value].sort()).toEqual(['stuff', 'things', 'wat'])
  })
  test('Visits a newly created Deliverable', async() => {
    const vulpes = genUser({
      username: 'Vulpes',
      landscape: true,
    })
    setViewer(store, vulpes)
    await router.push('/orders/Vulpes/order/1/deliverables/5/overview')
    const mockPush = vi.spyOn(router, 'push')
    wrapper = mount(
      WrappedDeliverableDetail, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Vulpes',
        },
      })
    const vm = wrapper.vm.$refs.vm as any
    const deliverable = genDeliverable()
    const order = deliverable.order
    order.seller = vulpes
    vm.deliverable.makeReady(deliverable)
    vm.order.makeReady(order)
    mockAxios.reset()
    vm.newInvoice.submitThen(vm.visitDeliverable)
    const newDeliverable = genDeliverable({id: 20})
    mockAxios.mockResponse(rs(newDeliverable))
    await flushPromises()
    await vm.$nextTick()
    expect(mockPush).toHaveBeenCalledWith({
      name: 'OrderDeliverableOverview',
      params: {
        orderId: '1',
        deliverableId: '20',
        username: 'Vulpes',
      },
    })
  })
  test('Determines whether an invoice should be marked escrow disabled', async() => {
    const vulpes = genUser({
      username: 'Vulpes',
      landscape: true,
    })
    setViewer(store, vulpes)
    await router.push('/orders/Vulpes/order/1/deliverables/5/overview')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['router-link'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Vulpes',
        },
      })
    const vm = wrapper.vm as any
    vm.deliverable.setX(genDeliverable())
    await vm.$nextTick()
    expect(vm.invoiceEscrowEnabled).toBe(false)
    vm.sellerHandler.artistProfile.makeReady(genArtistProfile())
    await vm.$nextTick()
    expect(vm.invoiceEscrowEnabled).toBe(true)
    vm.newInvoice.fields.paid.update(true)
    await vm.$nextTick()
    expect(vm.invoiceEscrowEnabled).toBe(false)
  })
  test('Takes the user to a new deliverable', async() => {
    const vulpes = genUser({
      username: 'Vulpes',
      landscape: true,
    })
    setViewer(store, vulpes)
    await router.push('/orders/Vulpes/order/1/deliverables/5/overview')
    const mockPush = vi.spyOn(router, 'push')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['router-link'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Vulpes',
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.deliverable.setX(genDeliverable())
    await vm.$nextTick()
    vm.visitDeliverable(genDeliverable({id: 100}))
    expect(mockPush).toHaveBeenCalledWith({
      name: 'OrderDeliverableOverview',
      params: {
        username: 'Vulpes',
        deliverableId: '100',
        orderId: deliverable.order.id + '',
      },
    })
    await vm.$nextTick()
  })
  test('Adds a new deliverable to the parent list', async() => {
    const vulpes = genUser({
      username: 'Vulpes',
      landscape: true,
    })
    setViewer(store, vulpes)
    await router.push('/orders/Vulpes/order/1/deliverables/5/overview')
    const mockPush = vi.spyOn(router, 'push')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['router-link'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Vulpes',
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable({id: 1})
    vm.deliverable.setX(deliverable)
    vm.parentDeliverables.setList([genDeliverable(({id: 1}))])
    await vm.$nextTick()
    vm.visitDeliverable(genDeliverable({id: 100}))
    await vm.$nextTick()
    expect(vm.parentDeliverables.list.length).toBe(2)
    expect(vm.parentDeliverables.list[1].x.id).toBe(100)
  })
  test('Sets the references on a new invoice', async() => {
    const fox = genUser({
      username: 'Fox',
      landscape: true,
    })
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/overview')
    const mockPush = vi.spyOn(router, 'push')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['router-link'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Sale',
          username: 'Fox',
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.deliverable.setX(genDeliverable())
    vm.references.setList([{
      id: 1,
      reference: genReference({id: 3}),
    }, {
      id: 2,
      reference: genReference({id: 4}),
    }])
    await vm.$nextTick()
    vm.newInvoice.keepReferences = false
    await vm.$nextTick()
    vm.newInvoice.keepReferences = true
    await vm.$nextTick()
    expect(vm.newInvoice.fields.references.value).toEqual([3, 4])
  })
  test('Determines the sellerName', async() => {
    const fox = genUser({
      username: 'Fox',
      landscape: true,
    })
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/overview')
    const mockPush = vi.spyOn(router, 'push')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['router-link'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Sale',
          username: 'Fox',
        },
      })
    const vm = wrapper.vm as any
    expect(vm.sellerName).toBe('')
    const deliverable = genDeliverable()
    vm.deliverable.setX(genDeliverable())
    await vm.$nextTick()
    expect(vm.sellerName).toBe('Vulpes')
  })
})
