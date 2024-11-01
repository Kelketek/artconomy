import {cleanUp, flushPromises, mount, rs, vueSetup, VuetifyWrapped, waitFor} from '@/specs/helpers/index.ts'
import {Router} from 'vue-router'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {deliverableRouter} from '@/components/views/order/specs/helpers.ts'
import {genDeliverable, genPowers, genUser} from '@/specs/helpers/fixtures.ts'
import DeliverableOverview from '@/components/views/order/deliverable/DeliverableOverview.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {ViewerType} from '@/types/enums/ViewerType.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {nextTick} from 'vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {setViewer} from '@/lib/lib.ts'
import {ViewerTypeValue} from '@/types/main'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let empty: VueWrapper<any>['vm']

const WrappedDeliverableOverview = VuetifyWrapped(DeliverableOverview)

describe('DeliverableOverview.vue', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
    empty = mount(Empty, vueSetup({store})).vm
  })
  const getDeliverable = (orderId: number, deliverableId: number) => {
    return {
      order: empty.$getSingle(`order${orderId}`),
      deliverable: empty.$getSingle(`order${orderId}__deliverable${deliverableId}`),
    }
  }
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Handles a null product', async() => {
    const user = genUser()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5/overview')
    wrapper = mount(
      WrappedDeliverableOverview, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager', 'ac-comment-section'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const deliverableDef = genDeliverable()
    deliverableDef.product = null
    const {
      order,
      deliverable,
    } = getDeliverable(1, 5)
    order.makeReady(deliverableDef.order)
    deliverable.makeReady(deliverableDef)
    await nextTick()
    await waitFor(() => expect(wrapper.text()).toContain('(Custom Project)'))
  })
  test('Sends an invite email', async() => {
    const user = genUser()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5/overview')
    wrapper = mount(
      WrappedDeliverableOverview, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager', 'ac-comment-section'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const deliverableDef = genDeliverable()
    deliverableDef.order.buyer = null
    deliverableDef.order.seller = user
    deliverableDef.order.customer_email = 'stuff@example.com'
    const {
      order,
      deliverable,
    } = getDeliverable(1, 5)
    order.makeReady(deliverableDef.order)
    deliverable.makeReady(deliverableDef)
    await nextTick()
    await flushPromises()
    mockAxios.reset()
    await wrapper.find('.send-invite-button').trigger('click')
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest.url).toBe('/api/sales/order/1/deliverables/5/invite/')
    mockAxios.mockResponse(rs(deliverableDef.order))
    await flushPromises()
    expect(wrapper.text()).toContain('Invite email sent!')
  })
  test('Loads with the order confirmation triggered', async() => {
    setViewer({ store, user: genUser() })
    await router.push('/orders/Fox/order/1/deliverables/5/overview?showConfirm=true')
    wrapper = mount(
      WrappedDeliverableOverview, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager', 'ac-comment-section'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const deliverableDef = genDeliverable()
    const {
      order,
      deliverable,
    } = getDeliverable(1, 5)
    order.makeReady(deliverableDef.order)
    deliverable.makeReady(deliverableDef)
    await nextTick()
    await waitFor(() => expect(wrapper.findComponent('.order-confirmation').isVisible()).toBe(true))
  })
  test.each`
  mode                  | string
  ${ViewerType.STAFF}  | ${'Staff'}
  ${ViewerType.SELLER} | ${'Seller'}
  ${ViewerType.BUYER}  | ${'Buyer'}
  ${ViewerType.UNSET}  | ${'Wat'}
  ${ViewerType.UNSET}  | ${''}
  `('Sets the viewerMode to $mode when $string is set as view_as.',
    async({
      mode,
      string,
    }: { mode: ViewerTypeValue, string: string }) => {
      setViewer({ store, user: genUser({ is_staff: true }), powers: genPowers({handle_disputes: true}) })
      await router.push(`/orders/Fox/order/1/deliverables/5/overview?view_as=${string}`)
      wrapper = mount(
        DeliverableOverview, {
          ...vueSetup({
            store,
            router,
            stubs: ['ac-revision-manager', 'ac-comment-section'],
          }),
          props: {
            orderId: 1,
            deliverableId: 5,
            baseName: 'Order',
            username: 'Fox',
          },
        })
      const vm = wrapper.vm as any
      await vm.$nextTick()
      expect(vm.viewSettings.x.viewerType).toBe(mode)
    })
})
