import {cleanUp, flushPromises, mount, rs, vueSetup, waitFor} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import DeliverableDetail from '@/components/views/order/DeliverableDetail.vue'
import {genDeliverable, genGuest, genPowers, genReference, genUser} from '@/specs/helpers/fixtures.ts'
import mockAxios from '@/__mocks__/axios.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import {DeliverableStatus} from '@/types/enums/DeliverableStatus.ts'
import {Router} from 'vue-router'
import {deliverableRouter} from '@/components/views/order/specs/helpers.ts'
import {genCharacter} from '@/store/characters/specs/fixtures.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {nextTick} from 'vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

const mockScrollIntoView = Element.prototype.scrollIntoView = vi.fn()

describe('DeliverableDetail.vue', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
    mockScrollIntoView.mockReset()
  })
  const getControllers = ({
    orderId,
    deliverableId,
  }: { orderId: string, deliverableId: string }) => {
    const empty = mount(Empty, vueSetup({store})).vm
    const baseName = `order${orderId}__deliverable${deliverableId}`
    return {
      deliverable: empty.$getSingle(baseName),
      order: empty.$getSingle(`order${orderId}`),
      viewSettings: empty.$getSingle(`${baseName}__viewSettings`),
      references: empty.$getList(`${baseName}__references`),
      revisions: empty.$getList(`${baseName}__revisions`),
      newInvoice: empty.$getForm(`${baseName}__addDeliverable`),
      addSubmission: empty.$getForm(`${baseName}__addSubmission`),
      parentDeliverables: empty.$getList(`order${orderId}__deliverables`),
    }
  }
  test('Handles a null buyer', async() => {
    const vulpes = genUser()
    vulpes.username = 'Fox'
    setViewer({ store, user: vulpes })
    await router.push('/orders/Fox/order/1/deliverables/5/')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Sale',
          username: 'Fox',
        },
      })
    const deliverableDef = genDeliverable()
    deliverableDef.order.buyer = null
    deliverableDef.order.seller = vulpes
    const deliverableRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/')
    mockAxios.mockResponse(rs(deliverableDef), deliverableRequest)
    await nextTick()
    expect(wrapper.text()).toContain('This order is pending your review.')
  })
  test('Sends a seller to their new submission', async() => {
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    setViewer({ store, user: vulpes })
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const deliverableDef = genDeliverable()
    deliverableDef.status = DeliverableStatus.COMPLETED
    const {deliverable} = getControllers({
      orderId: '1',
      deliverableId: '5',
    })
    deliverable.makeReady(deliverableDef)
    await nextTick()
    mockAxios.reset()
    await wrapper.find('.gallery-add').trigger('click')
    await nextTick()
    mockAxios.reset()
    await nextTick()
    await wrapper.findComponent('.dialog-submit').trigger('click')
    const newSubmission = genSubmission()
    newSubmission.id = 101
    const newSubmissionRequest = mockAxios.lastReqGet()
    expect(newSubmissionRequest.url).toBe('/api/sales/order/1/deliverables/5/outputs/')
    mockAxios.mockResponse(rs(newSubmission))
    await flushPromises()
    await nextTick()
    expect(router.currentRoute.value.name).toBe('Submission')
    expect(router.currentRoute.value.params).toEqual({submissionId: '101'})
    expect(router.currentRoute.value.query).toEqual({editing: 'true'})
  })
  test('Handles an order without a product', async() => {
    setViewer({ store, user: genUser() })
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const deliverableDef = genDeliverable()
    deliverableDef.product = null
    deliverableDef.status = DeliverableStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/')
    mockAxios.mockResponse(rs(deliverableDef), orderRequest)
    await flushPromises()
    await nextTick()
  })
  test('Renders a view mode selector', async() => {
    const user = genUser({is_staff: true})
    user.username = 'Dude'
    setViewer({ store, user, powers: genPowers({handle_disputes: true}) })
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const deliverableDef = genDeliverable()
    deliverableDef.product = null
    deliverableDef.status = DeliverableStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/')
    mockAxios.mockResponse(rs(deliverableDef), orderRequest)
    await flushPromises()
    await nextTick()
    const selector = wrapper.find('.view-mode-select')
    expect(selector.exists()).toBe(true)
    expect(selector.text()).contains('Please select...')
  })
  test('Prompts to add revision to collection', async() => {
    setViewer({ store, user: genUser() })
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const deliverableDef = genDeliverable()
    deliverableDef.product = null
    deliverableDef.status = DeliverableStatus.COMPLETED
    deliverableDef.revisions_hidden = false
    const {deliverable} = getControllers({
      orderId: '1',
      deliverableId: '5',
    })
    deliverable.makeReady(deliverableDef)
    await nextTick()
    await wrapper.find('.collection-add').trigger('click')
    await nextTick()
    expect(wrapper.findComponent('.add-submission-dialog').isVisible()).toBe(true)
  })
  test('Prompts to add revision to collection by registering if they are a guest', async() => {
    const user = genGuest()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const deliverableDef = genDeliverable()
    deliverableDef.order.buyer = {...user}
    deliverableDef.product = null
    deliverableDef.status = DeliverableStatus.COMPLETED
    deliverableDef.order.claim_token = 'sdvi397awr'
    deliverableDef.revisions_hidden = false
    const {deliverable} = getControllers({
      orderId: '1',
      deliverableId: '5',
    })
    deliverable.makeReady(deliverableDef)
    await nextTick()
    await wrapper.find('.collection-add').trigger('click')
    await nextTick()
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toEqual(
      '/login/register/?claim=sdvi397awr&next=/orders/Fox/order/1/deliverables/5/?showAdd=true',
    )
  })
  test('Does not have the submission adding form loaded by default', async() => {
    const user = genUser()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const {deliverable} = getControllers({
      orderId: '1',
      deliverableId: '5',
    })
    const deliverableDef = genDeliverable()
    deliverableDef.order.seller = user
    deliverable.makeReady(deliverableDef)
    await nextTick()
    expect(wrapper.find('.add-submission-dialog').exists()).toBe(false)
  })
  test('Loads with the submission prompt triggered', async() => {
    const user = genUser({username: 'Beep'})
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5?showAdd=true')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const {deliverable} = getControllers({
      orderId: '1',
      deliverableId: '5',
    })
    const deliverableDef = genDeliverable()
    deliverableDef.order.seller = user
    deliverable.makeReady(deliverableDef)
    await nextTick()
    expect(wrapper.findComponent('.add-submission-dialog').isVisible()).toBe(true)
  })
  test('Prompts to link a guest account', async() => {
    const user = genGuest()
    user.username = '__1'
    setViewer({ store, user })
    await router.push('/orders/__1/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: '__1',
        },
      })
    const deliverableDef = genDeliverable()
    deliverableDef.order.buyer = {...user}
    deliverableDef.order.claim_token = 'sdvi397awr'
    deliverableDef.revisions_hidden = false
    const {deliverable} = getControllers({
      orderId: '1',
      deliverableId: '5',
    })
    deliverable.makeReady(deliverableDef)
    await nextTick()
    await wrapper.find('.link-account').trigger('click')
    await nextTick()
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toEqual(
      '/login/register/?claim=sdvi397awr&next=/orders/__1/order/1/deliverables/5/',
    )
  })
  test('Adds character tags to submission form', async() => {
    setViewer({ store, user: genUser() })
    await router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const {
      deliverable,
      revisions,
      addSubmission,
    } = getControllers({
      orderId: '1',
      deliverableId: '5',
    })
    deliverable.makeReady(genDeliverable())
    revisions.makeReady([])
    await nextTick()
    const characterRequest = mockAxios.getReqByUrl('/api/sales/order/1/deliverables/5/characters/')
    const character = genCharacter()
    character.tags = ['stuff', 'things', 'wat']
    mockAxios.mockResponse(rs([{
      id: 1,
      character,
    }]), characterRequest)
    await flushPromises()
    await nextTick()
    expect([...addSubmission.fields.tags.value].sort()).toEqual(['stuff', 'things', 'wat'])
  })
  test('Handles a newly created deliverable', async() => {
    const vulpes = genUser({
      username: 'Vulpes',
      landscape: true,
    })
    setViewer({ store, user: vulpes })
    await router.push('/orders/Vulpes/order/1/deliverables/5/overview')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['router-link'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Order',
          username: 'Vulpes',
        },
      })
    const deliverableDef = genDeliverable({id: 1})
    const {
      deliverable,
      parentDeliverables,
      viewSettings,
    } = getControllers({
      orderId: '1',
      deliverableId: '5',
    })
    deliverable.makeReady(deliverableDef)
    parentDeliverables.setList([genDeliverable(({id: 1}))])
    viewSettings.patchers.showAddDeliverable.model = true
    await nextTick()
    mockAxios.reset()
    await waitFor(() => wrapper.findComponent('.add-deliverable-dialog .dialog-submit').trigger('click'))
    mockAxios.mockResponse(rs(genDeliverable({id: 100})))
    await waitFor(() => expect(parentDeliverables.list.length).toBe(2))
    expect(parentDeliverables.list[1].x.id).toBe(100)
    expect(router.currentRoute.value.name).toEqual('OrderDeliverableOverview')
    expect(router.currentRoute.value.params).toEqual({
      orderId: '1',
      deliverableId: '100',
      username: 'Vulpes',
    })
  })
  test('Sets the references on a new invoice', async() => {
    const fox = genUser({
      username: 'Fox',
      landscape: true,
    })
    setViewer({ store, user: fox })
    await router.push('/orders/Fox/order/1/deliverables/5/overview')
    wrapper = mount(
      DeliverableDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['router-link'],
        }),
        props: {
          orderId: '1',
          deliverableId: '5',
          baseName: 'Sale',
          username: 'Fox',
        },
      })
    const {
      deliverable,
      references,
      newInvoice,
    } = getControllers({
      orderId: '1',
      deliverableId: '5',
    })
    deliverable.makeReady(genDeliverable())
    references.setList([{
      id: 1,
      reference: genReference({id: 3}),
    }, {
      id: 2,
      reference: genReference({id: 4}),
    }])
    await nextTick()
    newInvoice.keepReferences = false
    await nextTick()
    newInvoice.keepReferences = true
    await nextTick()
    expect(newInvoice.fields.references.value).toEqual([3, 4])
  })
})
