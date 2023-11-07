import {cleanUp, flushPromises, mount, rs, setViewer, vueSetup, VuetifyWrapped} from '@/specs/helpers'
import {Router} from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import {deliverableRouter} from '@/components/views/order/specs/helpers'
import {genDeliverable, genUser} from '@/specs/helpers/fixtures'
import DeliverableOverview from '@/components/views/order/deliverable/DeliverableOverview.vue'
import mockAxios from '@/__mocks__/axios'
import {VIEWER_TYPE} from '@/types/VIEWER_TYPE'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

const WrappedDeliverableOverview = VuetifyWrapped(DeliverableOverview)

describe('DeliverableOverview.vue', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Handles a null product', async() => {
    const user = genUser()
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/deliverables/5/overview')
    wrapper = mount(
      WrappedDeliverableOverview, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager', 'ac-comment-section'],
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
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.name).toBe('(Custom Project)')
  })
  test('Sends an invite email', async() => {
    const user = genUser()
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/deliverables/5/overview')
    wrapper = mount(
      WrappedDeliverableOverview, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager', 'ac-comment-section'],
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
    deliverable.order.buyer = null
    deliverable.order.seller = user
    deliverable.order.customer_email = 'stuff@example.com'
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    mockAxios.reset()
    await wrapper.find('.send-invite-button').trigger('click')
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest.url).toBe('/api/sales/order/1/deliverables/5/invite/')
    mockAxios.mockResponse(rs(deliverable.order))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.inviteSent).toBe(true)
  })
  test('Loads with the order confirmation triggered', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/deliverables/5/overview?showConfirm=true')
    wrapper = mount(
      WrappedDeliverableOverview, {
        ...vueSetup({
          store,
          extraPlugins: [router],
          stubs: ['ac-revision-manager', 'ac-comment-section'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const vm = wrapper.vm.$refs.vm as any
    await vm.$nextTick()
    expect(vm.showConfirm).toBe(true)
  })
  test.each`
  mode                  | string
  ${VIEWER_TYPE.STAFF}  | ${'Staff'}
  ${VIEWER_TYPE.SELLER} | ${'Seller'}
  ${VIEWER_TYPE.BUYER}  | ${'Buyer'}
  ${VIEWER_TYPE.UNSET}  | ${'Wat'}
  ${VIEWER_TYPE.UNSET}  | ${''}
  `('Sets the viewerMode to $mode when $string is set as view_as.',
    async({
      mode,
      string,
    }: { mode: VIEWER_TYPE, string: string }) => {
      setViewer(store, genUser({is_staff: true}))
      await router.push(`/orders/Fox/order/1/deliverables/5/overview?view_as=${string}`)
      wrapper = mount(
        DeliverableOverview, {
          ...vueSetup({
            store,
            extraPlugins: [router],
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
