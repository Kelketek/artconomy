import {genDeliverable, genRevision, genUser} from '@/specs/helpers/fixtures.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {Router} from 'vue-router'
import {ArtStore, createStore} from '@/store/index.ts'
import {deliverableRouter} from '@/components/views/order/specs/helpers.ts'
import DeliverableRevisions from '@/components/views/order/deliverable/DeliverableRevisions.vue'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe('DeliverableRevisions.vue', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Determines the final', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/revisions')
    wrapper = mount(
      DeliverableRevisions, {
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
  test('Refreshes the deliverable when the list changes', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/revisions')
    wrapper = mount(
      DeliverableRevisions, {
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
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    vm.revisions.setList([])
    vm.revisions.ready = true
    vm.revisions.fetching = false
    const spyRefresh = vi.spyOn(vm.deliverable, 'refresh')
    await vm.$nextTick()
    expect(spyRefresh).not.toHaveBeenCalled()
    vm.revisions.uniquePush(genRevision())
    await vm.$nextTick()
    expect(spyRefresh).toHaveBeenCalled()
  })
  test('Fetches revisions if they are newly permitted to be seen', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/deliverables/5/revisions')
    wrapper = mount(
      DeliverableRevisions, {
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
    const mockGet = vi.spyOn(vm.revisions, 'get')
    vm.deliverable.updateX({revisions_hidden: false})
    await vm.$nextTick()
    expect(mockGet).toHaveBeenCalled()
  })
})
