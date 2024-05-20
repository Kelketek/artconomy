import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {
  cleanUp,
  confirmAction, createTestRouter,
  flushPromises,
  mount,
  rs,
  vueSetup, waitFor,
} from '@/specs/helpers/index.ts'
import {genAnon, genUser} from '@/specs/helpers/fixtures.ts'
import {Router} from 'vue-router'
import mockAxios from '@/__mocks__/axios.ts'
import {User} from '@/store/profiles/types/User.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import SubmissionDetail from '@/components/views/submission/SubmissionDetail.vue'
import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'
import {searchSchema, setViewer} from '@/lib/lib.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {nextTick} from 'vue'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let vulpes: User


describe('SubmissionDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    vulpes = genUser()
    router = createTestRouter()
    vulpes.username = 'Vulpes'
    vulpes.is_staff = false
    vulpes.is_superuser = false
    vulpes.id = 2
    vulpes.artist_mode = false
    mount(Empty, vueSetup({store})).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Deletes the submission', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    await router.push(`/submissions/${submission.id}`)
    submission.owner = vulpes as RelatedUser
    wrapper = mount(SubmissionDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm
    vm.submission.makeReady(submission)
    mockAxios.reset()
    await nextTick()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    const deleteRequest = mockAxios.lastReqGet()
    expect(deleteRequest.method === 'delete')
    mockAxios.mockResponse(rs(null, {status: 204}), deleteRequest)
    await flushPromises()
    await nextTick()
    await flushPromises()
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('Profile')
  })
  test('Sets the meta info with artists', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = 'Test submission'
    submission.owner = vulpes as RelatedUser
    wrapper = mount(SubmissionDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.artists.setList([{user: genUser()}])
    vm.artists.ready = true
    vm.artists.fetching = false
    mockAxios.reset()
    await nextTick()
    expect(document.title).toEqual('Test submission -- by Fox - (Artconomy.com)')
  })
  test('Sets the meta info with artists and no title', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner = vulpes as RelatedUser
    wrapper = mount(SubmissionDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.artists.setList([{user: genUser()}])
    vm.artists.ready = true
    vm.artists.fetching = false
    mockAxios.reset()
    await nextTick()
    expect(document.title).toEqual('By Fox - (Artconomy.com)')
  })
  test('Shows a rating edit dialog', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner = vulpes as RelatedUser
    await router.push({
      name: 'Submission',
      params: {submissionId: submission.id},
    })
    wrapper = mount(SubmissionDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm
    vm.submission.makeReady(submission)
    vm.editing = true
    await flushPromises()
    mockAxios.reset()
    await vm.$nextTick()
    const ratingButton = wrapper.findComponent('.rating-button')
    await ratingButton.trigger('click')
    await nextTick()
    await waitFor(() => expect(wrapper.findComponent('.rating-field').exists()).toBe(true))
  })
  test('Nudges the viewer to adjust their settings', async() => {
    setViewer(store, genAnon())
    const submission = genSubmission({
      rating: 2,
      id: 123,
    })
    wrapper = mount(SubmissionDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm
    vm.submission.makeReady(submission)
    await nextTick()
    expect(store.state.showAgeVerification).toBe(true)
  })
  test('Reports that the viewer tag-controls the piece if the owner is taggable', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner.taggable = true
    wrapper = mount(SubmissionDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm
    vm.submission.makeReady(submission)
    mockAxios.reset()
    await nextTick()
    expect(vm.tagControls).toBe(true)
  })
  test('Reports that the viewer does not tag-control the piece if the owner is not taggable', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner.taggable = false
    wrapper = mount(SubmissionDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.editing = true
    mockAxios.reset()
    await nextTick()
    expect(vm.tagControls).toBe(false)
  })
  test('Shows a context menu when the user controls the submission', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.owner = vulpes
    wrapper = mount(SubmissionDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.more-button').exists()).toBe(true)
  })
  test('Does not show a context menu when the user does not control', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    wrapper = mount(SubmissionDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.more-button').exists()).toBe(false)
  })
})
