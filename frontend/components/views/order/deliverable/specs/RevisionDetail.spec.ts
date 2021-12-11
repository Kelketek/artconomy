import {cleanUp, createVuetify, docTarget, mount, setViewer, vueSetup} from '@/specs/helpers'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
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
  it('Determines if the revision is the most recent one', async() => {
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
        attachTo: docTarget(),
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
  it('Determines if the revision is the final', async() => {
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
        attachTo: docTarget(),
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
  it('Determines if the revision has a submission in the current user\'s gallery', async() => {
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
        attachTo: docTarget(),
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    const revision = genRevision({id: 3, submissions: []})
    vm.revisions.makeReady([revision])
    vm.revision.makeReady(revision)
    await vm.$nextTick()
    expect(vm.gallerySubmissionId).toBe(null)
    expect(vm.isSubmitted).toBe(false)
    expect(vm.galleryLink).toBe(null)
    vm.revision.updateX({submissions: [{owner_id: user.id, id: 5}]})
    await vm.$nextTick()
    expect(vm.gallerySubmissionId).toBe(5)
    expect(vm.isSubmitted).toBe(true)
    expect(vm.galleryLink).toEqual({name: 'Submission', params: {submissionId: '5'}})
    vm.deliverable.updateX({final_uploaded: true})
    await vm.$nextTick()
    expect(vm.isFinal).toBe(true)
  })
  it('Shows the submission button to a buyer only once the deliverable is completed', async() => {
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
        attachTo: docTarget(),
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    const revision = genRevision({id: 3, submissions: []})
    vm.revisions.makeReady([revision])
    vm.revision.makeReady(revision)
    await vm.$nextTick()
    expect(wrapper.find('.prep-submission-button').exists()).toBe(false)
    vm.deliverable.updateX({status: DeliverableStatus.COMPLETED})
    await vm.$nextTick()
    expect(wrapper.find('.prep-submission-button').exists()).toBe(true)
  })
  it('Prepares a revision for publication to gallery', async() => {
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
        attachTo: docTarget(),
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable({status: DeliverableStatus.COMPLETED})
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    const revision = genRevision({id: 3, submissions: []})
    vm.revisions.makeReady([revision])
    vm.revision.makeReady(revision)
    await vm.$nextTick()
    expect(vm.addSubmission.fields.revision.value).toBe(null)
    expect(vm.viewSettings.patchers.showAddSubmission.model).toBe(false)
    wrapper.find('.prep-submission-button').trigger('click')
    await vm.$nextTick()
    expect(vm.addSubmission.fields.revision.value).toBe(3)
    expect(vm.viewSettings.patchers.showAddSubmission.model).toBe(true)
  })
  it('Determines if the deliverable has been archived', async() => {
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
        attachTo: docTarget(),
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
