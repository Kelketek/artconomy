import {cleanUp, flushPromises, mount, rs, vueSetup} from '@/specs/helpers/index.ts'
import {Router} from 'vue-router'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {deliverableRouter} from '@/components/views/order/specs/helpers.ts'
import {genDeliverable, genRevision, genUser} from '@/specs/helpers/fixtures.ts'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import RevisionDetail from '@/components/views/order/deliverable/RevisionDetail.vue'
import Revision from '@/types/Revision.ts'
import {SingleController} from '@/store/singles/controller.ts'
import mockAxios from '@/specs/helpers/mock-axios.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe('DeliverableOverview.vue', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Determines if the revision is the most recent one', async() => {
    const user = genUser()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
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
          revisionId: 3,
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
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
  test('Determines if the revision is the final', async() => {
    const user = genUser()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
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
          revisionId: 3,
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
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
  test('Determines if the revision has a submission in the current user\'s gallery', async() => {
    const user = genUser()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
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
          revisionId: 3,
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    const revision = genRevision({
      id: 3,
      submissions: [],
    })
    vm.revisions.makeReady([revision])
    vm.revision.makeReady(revision)
    await vm.$nextTick()
    expect(vm.gallerySubmissionId).toBe(null)
    expect(vm.isSubmitted).toBe(false)
    expect(vm.galleryLink).toBe(null)
    vm.revision.updateX({
      submissions: [{
        owner_id: user.id,
        id: 5,
      }],
    })
    await vm.$nextTick()
    expect(vm.gallerySubmissionId).toBe(5)
    expect(vm.isSubmitted).toBe(true)
    expect(vm.galleryLink).toEqual({
      name: 'Submission',
      params: {submissionId: '5'},
    })
    vm.deliverable.updateX({final_uploaded: true})
    await vm.$nextTick()
    expect(vm.isFinal).toBe(true)
  })
  test('Shows the submission button to a buyer only once the deliverable is completed', async() => {
    const user = genUser()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
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
          revisionId: 3,
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    const revision = genRevision({
      id: 3,
      submissions: [],
    })
    vm.revisions.makeReady([revision])
    vm.revision.makeReady(revision)
    await vm.$nextTick()
    expect(wrapper.find('.prep-submission-button').exists()).toBe(false)
    vm.deliverable.updateX({status: DeliverableStatus.COMPLETED})
    await vm.$nextTick()
    expect(wrapper.find('.prep-submission-button').exists()).toBe(true)
  })
  test('Prepares a revision for publication to gallery', async() => {
    const user = genUser()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
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
          revisionId: 3,
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable({status: DeliverableStatus.COMPLETED})
    vm.deliverable.makeReady(deliverable)
    await vm.$nextTick()
    expect(vm.isLast).toBe(false)
    const revision = genRevision({
      id: 3,
      submissions: [],
    })
    vm.revisions.makeReady([revision])
    vm.revision.makeReady(revision)
    await vm.$nextTick()
    expect(vm.addSubmission.fields.revision.value).toBe(null)
    expect(vm.viewSettings.patchers.showAddSubmission.model).toBe(false)
    await wrapper.find('.prep-submission-button').trigger('click')
    await vm.$nextTick()
    expect(vm.addSubmission.fields.revision.value).toBe(3)
    expect(vm.viewSettings.patchers.showAddSubmission.model).toBe(true)
  })
  test('Determines if the deliverable has been archived', async() => {
    const user = genUser()
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
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
          revisionId: 3,
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    deliverable.status = DeliverableStatus.IN_PROGRESS
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
  test('Deletes a revision and removes it from the list of revisions', async() => {
    const user = genUser({
      username: 'Fox',
      is_staff: false,
    })
    setViewer({ store, user })
    await router.push('/orders/Fox/order/1/deliverables/5/revisions/3/')
    wrapper = mount(
      RevisionDetail, {
        ...vueSetup({
          store,
          router,
          stubs: ['ac-revision-manager', 'ac-comment-section'],
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Sale',
          username: 'Fox',
          revisionId: 3,
        },
      })
    const vm = wrapper.vm as any
    const deliverable = genDeliverable()
    deliverable.status = DeliverableStatus.IN_PROGRESS
    deliverable.order.seller = user
    deliverable.order.buyer = genUser({username: 'Vulpes'})
    vm.deliverable.makeReady(deliverable)
    const revision = genRevision({id: 1})
    vm.revision.makeReady(revision)
    const otherRevisions = [genRevision({id: 2}), genRevision({id: 3})]
    vm.revisions.makeReady([...otherRevisions, revision])
    await vm.$nextTick()
    await flushPromises()
    mockAxios.reset()
    await wrapper.find('.delete-revision').trigger('click')
    await vm.$nextTick()
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest.method).toBe('delete')
    mockAxios.mockResponse(rs({}))
    await vm.$nextTick()
    const remaining = vm.revisions.list.map((rev: SingleController<Revision>) => ({...rev.x}))
    expect(remaining).toEqual(otherRevisions)
  })
})
