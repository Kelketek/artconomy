import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {Vuetify} from 'vuetify'
import {deliverableRouter} from '@/components/views/order/specs/helpers'
import {genDeliverable, genRevision, genUser} from '@/specs/helpers/fixtures'
import {DeliverableStatus} from '@/types/DeliverableStatus'
import RevisionDetail from '@/components/views/order/deliverable/RevisionDetail.vue'

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
  it('Determines if the revision is the most recent one', async () => {
    const user = genUser()
    setViewer(store, user)
    router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox', revisionId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    const revision = genRevision({id: 3})
    vm.revisions.setList([])
    vm.fetching = false
    vm.ready = true
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    vm.revision.makeReady(revision)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    vm.revisions.push(genRevision({id: 5}))
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    vm.revisions.push(revision)
    await vm.$nextTick()
    expect(vm.isLast).toBe(true)
  })
  it('Determines if the revision is the final', async () => {
    const user = genUser()
    setViewer(store, user)
    router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox', revisionId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    const revision = genRevision({id: 3})
    vm.revisions.setList([revision])
    vm.fetching = false
    vm.ready = true
    vm.revision.makeReady(revision)
    await vm.$nextTick()
    expect(vm.isFinal).toBe(false)
    vm.deliverable.updateX({final_uploaded: true})
    await vm.$nextTick()
    expect(vm.isFinal).toBe(true)
  })
  it('Determines if the deliverable has been archived', async () => {
    const user = genUser()
    setViewer(store, user)
    router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox', revisionId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    deliverable.status = DeliverableStatus.IN_PROGRESS
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    const revision = genRevision({id: 3})
    vm.revisions.setList([revision])
    vm.fetching = false
    vm.ready = true
    vm.revision.makeReady(revision)
    await vm.$nextTick()
    expect(vm.archived).toBe(false)
    vm.deliverable.updateX({status: DeliverableStatus.COMPLETED})
    await vm.$nextTick()
    expect(vm.archived).toBe(true)
    vm.deliverable.updateX({status: DeliverableStatus.CANCELLED})
    await vm.$nextTick()
    expect(vm.archived).toBe(true)
    vm.deliverable.updateX({status: DeliverableStatus.REFUNDED})
    await vm.$nextTick()
    expect(vm.archived).toBe(true)
  })
})
