import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {
  cleanUp,
  confirmAction, createVuetify, docTarget,
  flushPromises,
  rs,
  setViewer,
  vueSetup,
} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Router from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import {User} from '@/store/profiles/types/User'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Submission from '@/types/Submission'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import SubmissionDetail from '@/components/views/submission/SubmissionDetail.vue'
import {RelatedUser} from '@/store/profiles/types/RelatedUser'
import {searchSchema} from '@/lib/lib'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vulpes: User
let vuetify: Vuetify

describe('SubmissionDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    vulpes = genUser()
    vulpes.username = 'Vulpes'
    vulpes.is_staff = false
    vulpes.is_superuser = false
    vulpes.id = 2
    vulpes.artist_mode = false
    vuetify = createVuetify()
    router = new Router({
      mode: 'history',
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
      ],
    })
    mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Deletes the submission', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.owner = vulpes as RelatedUser
    wrapper = mount(SubmissionDetail, {
      localVue, store, router, vuetify, propsData: {submissionId: '123'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    await vm.$nextTick()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    mockAxios.mockResponse(rs(null, {status: 204}))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.$route.name).toBe('Profile')
  })
  it('Sets the meta info with artists', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = 'Test submission'
    submission.owner = vulpes as RelatedUser
    wrapper = mount(SubmissionDetail, {
      localVue, store, router, vuetify, propsData: {submissionId: '123'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
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
  it('Sets the meta info with artists and no title', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner = vulpes as RelatedUser
    wrapper = mount(SubmissionDetail, {
      localVue, store, router, vuetify, propsData: {submissionId: '123'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
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
  it('Shows a rating edit dialog', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner = vulpes as RelatedUser
    wrapper = mount(SubmissionDetail, {
      localVue, store, router, vuetify, propsData: {submissionId: '123'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.editing = true
    mockAxios.reset()
    await vm.$nextTick()
    wrapper.find('.rating-button').trigger('click')
    await vm.$nextTick()
    expect(vm.ratingDialog).toBe(true)
  })
  it('Does not show a rating edit dialog if not in editing mode', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner = vulpes as RelatedUser
    wrapper = mount(SubmissionDetail, {
      localVue, store, router, vuetify, propsData: {submissionId: '123'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.editing = false
    mockAxios.reset()
    await vm.$nextTick()
    wrapper.find('.rating-button').trigger('click')
    await vm.$nextTick()
    expect(vm.ratingDialog).toBe(false)
  })
  it('Reports that the viewer tag-controls the piece if the owner is taggable', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner.taggable = true
    wrapper = mount(SubmissionDetail, {
      localVue, store, router, vuetify, propsData: {submissionId: '123'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.editing = true
    mockAxios.reset()
    await vm.$nextTick()
    expect(vm.tagControls).toBe(true)
  })
  it('Reports that the viewer does not tag-control the piece if the owner is not taggable', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.title = ''
    submission.owner.taggable = false
    wrapper = mount(SubmissionDetail, {
      localVue, store, router, vuetify, propsData: {submissionId: '123'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    vm.editing = true
    mockAxios.reset()
    await vm.$nextTick()
    expect(vm.tagControls).toBe(false)
  })
  it('Shows a context menu when the user controls the submission', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    submission.owner = vulpes
    wrapper = mount(SubmissionDetail, {
      localVue, store, router, vuetify, propsData: {submissionId: '123'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.more-button').exists()).toBe(true)
  })
  it('Does not show a context menu when the user does not control', async() => {
    setViewer(store, vulpes)
    const submission = genSubmission()
    wrapper = mount(SubmissionDetail, {
      localVue, store, router, vuetify, propsData: {submissionId: '123'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.submission.setX(submission)
    vm.submission.fetching = false
    vm.submission.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.more-button').exists()).toBe(false)
  })
})
