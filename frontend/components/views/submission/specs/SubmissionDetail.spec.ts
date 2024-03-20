import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {
  cleanUp,
  confirmAction,
  flushPromises,
  mount,
  rs,
  vueSetup, VuetifyWrapped,
} from '@/specs/helpers/index.ts'
import {genAnon, genUser} from '@/specs/helpers/fixtures.ts'
import {createRouter, createWebHistory, Router} from 'vue-router'
import mockAxios from '@/__mocks__/axios.ts'
import {User} from '@/store/profiles/types/User.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import SubmissionDetail from '@/components/views/submission/SubmissionDetail.vue'
import {RelatedUser} from '@/store/profiles/types/RelatedUser.ts'
import {searchSchema, setViewer} from '@/lib/lib.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let vulpes: User

const WrappedSubmissionDetail = VuetifyWrapped(SubmissionDetail)

describe('SubmissionDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    vulpes = genUser()
    vulpes.username = 'Vulpes'
    vulpes.is_staff = false
    vulpes.is_superuser = false
    vulpes.id = 2
    vulpes.artist_mode = false
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          name: 'Order',
          path: '/order/:username/:orderId/',
          props: true,
          component: Empty,
        },
        {
          path: '/profile/:username',
          component: Empty,
          name: 'Profile',
          props: true,
          children: [{
            path: 'about',
            name: 'AboutUser',
            component: Empty,
            props: true,
          }, {
            path: 'products',
            name: 'Products',
            component: Empty,
            props: true,
          }],
        }, {
          path: '/submissions/:submissionId',
          name: 'Submission',
          component: Empty,
          props: true,
        },
        {
          path: '/search/submissions/',
          name: 'SearchSubmissions',
          component: Empty,
          props: true,
        },
        {
          path: '/',
          name: 'Home',
          component: Empty,
          props: true,
        },
      ],
    })
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
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.submission.makeReady(submission)
    mockAxios.reset()
    await vm.$nextTick()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    const deleteRequest = mockAxios.lastReqGet()
    expect(deleteRequest.method === 'delete')
    mockAxios.mockResponse(rs(null, {status: 204}), deleteRequest)
    await flushPromises()
    await vm.$nextTick()
    await flushPromises()
    await router.isReady()
    expect(router.currentRoute.value.name).toBe('Profile')
  })
  test('Sets the meta info with artists', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = 'Test submission'
    submission.owner = vulpes as RelatedUser
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.artists.setList([{user: genUser()}])
    vm.artists.ready = true
    vm.artists.fetching = false
    mockAxios.reset()
    await vm.$nextTick()
    expect(document.title).toEqual('Test submission -- by Fox - (Artconomy.com)')
  })
  test('Sets the meta info with artists and no title', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner = vulpes as RelatedUser
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.artists.setList([{user: genUser()}])
    vm.artists.ready = true
    vm.artists.fetching = false
    mockAxios.reset()
    await vm.$nextTick()
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
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.submission.makeReady(submission)
    vm.editing = true
    await flushPromises()
    mockAxios.reset()
    await vm.$nextTick()
    wrapper.find('.rating-button').trigger('click')
    await vm.$nextTick()
    expect(vm.ratingDialog).toBe(true)
  })
  test('Nudges the viewer to adjust their settings', async() => {
    setViewer(store, genAnon())
    const submission = genSubmission({
      rating: 2,
      id: 123,
    })
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    const mockAgeCheck = vi.spyOn(vm, 'ageCheck')
    vm.submission.makeReady(submission)
    await vm.$nextTick()
    expect(mockAgeCheck).toHaveBeenCalledWith({value: 2})
  })
  test('Does not show a rating edit dialog if not in editing mode', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner = vulpes as RelatedUser
    await router.push({
      name: 'Submission',
      params: {submissionId: submission.id},
      query: {editing: 'true'},
    })
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.submission.makeReady(submission)
    vm.editing = false
    await flushPromises()
    mockAxios.reset()
    await vm.$nextTick()
    expect(vm.editing).toBe(false)
    await wrapper.find('.rating-button').trigger('click')
    await vm.$nextTick()
    expect(vm.ratingDialog).toBe(false)
  })
  test('Reports that the viewer tag-controls the piece if the owner is taggable', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner.taggable = true
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.submission.makeReady(submission)
    mockAxios.reset()
    await vm.$nextTick()
    expect(vm.tagControls).toBe(true)
  })
  test('Reports that the viewer does not tag-control the piece if the owner is not taggable', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner.taggable = false
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.editing = true
    mockAxios.reset()
    await vm.$nextTick()
    expect(vm.tagControls).toBe(false)
  })
  test('Shows a context menu when the user controls the submission', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.owner = vulpes
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.more-button').exists()).toBe(true)
  })
  test('Does not show a context menu when the user does not control', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    wrapper = mount(WrappedSubmissionDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
        stubs: ['ac-comment'],
      }),
      props: {submissionId: '123'},
    })
    const vm = wrapper.vm.$refs.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.more-button').exists()).toBe(false)
  })
})
