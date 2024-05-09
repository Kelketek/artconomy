import {VueWrapper} from '@vue/test-utils'
import {
  cleanUp,
  createTestRouter,
  flushPromises,
  mount,
  rs,
  vueSetup,
  VuetifyWrapped,
  waitFor,
} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import DummySubmit from '@/components/specs/DummySubmit.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {nextTick} from 'vue'
import {setViewer} from '@/lib/lib.ts'
import {router} from '@/router'
import {useForm} from '@/store/forms/hooks.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'

let wrapper: VueWrapper<any>
let store: ArtStore

const mockError = vi.spyOn(console, 'error')

const WrappedDummySubmit = VuetifyWrapped(DummySubmit)

describe('AcNewSubmission.vue', () => {
  beforeEach(() => {
    store = createStore()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts the submission form', async() => {
    setViewer(store, genUser())
    wrapper = mount(DummySubmit, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Fox'},
            query: {editing: false},
          },
        },
      }),
      props: {username: 'Fox'},
    })
  })
  test('Toggles the isArtist computed field', async() => {
    const user = genUser()
    user.id = 1
    setViewer(store, user)
    wrapper = mount(DummySubmit, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Fox'},
            query: {editing: false},
          },
        },
      }),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    await waitFor(() => expect(vm.$refs.submissionForm).toBeTruthy())
    const form = vm.$refs.submissionForm
    expect(form.newUpload.fields.artists.value).toEqual([])
    expect(form.isArtist).toBe(false)
    form.isArtist = true
    await form.$nextTick()
    expect(form.isArtist).toBe(true)
    expect(form.newUpload.fields.artists.value).toEqual([1])
    form.isArtist = true
    expect(form.newUpload.fields.artists.value).toEqual([1])
    form.isArtist = false
    await form.$nextTick()
    expect(form.isArtist).toBe(false)
    expect(form.newUpload.fields.artists.value).toEqual([])
  })
  test('Submits and pushes you to the new Submission', async() => {
    const user = genUser()
    user.id = 1
    setViewer(store, user)
    const router = createTestRouter()
    await router.push({name: 'Profile', params: {username: 'Fox'}, query: {editing: 'false'}})
    wrapper = mount(WrappedDummySubmit, {
      ...vueSetup({
        store,
        router,
      }),
      props: {username: 'Fox'},
    })
    await nextTick()
    mockAxios.reset()
    const empty = mount(Empty, vueSetup({store})).vm
    const form = empty.$getForm('newUpload')
    form.step = 2
    await nextTick()
    await wrapper.findComponent('.submit-button').trigger('click')
    expect(mockAxios.request).toHaveBeenCalled()
    const submission = genSubmission()
    submission.id = 3
    mockAxios.mockResponse(rs(submission))
    await waitFor(() => expect(router.currentRoute.value.name).toBe('Submission'))
    expect(router.currentRoute.value.params).toEqual({submissionId: '3'})
    expect(router.currentRoute.value.query).toEqual({editing: 'true'})
  })
  test('Submits and resets if multi-upload is enabled', async() => {
    const user = genUser()
    user.id = 1
    setViewer(store, user)
    const mockPush = vi.fn()
    wrapper = mount(DummySubmit, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Fox'},
            query: {editing: 'false'},
          },
          $router: {push: mockPush},
        },
      }),
      props: {
        username: 'Fox',
        allowMultiple: true,
      },
    })
    const vm = wrapper.vm as any
    await nextTick()
    mockAxios.reset()
    await waitFor(() => expect(vm.$refs.submissionForm).toBeTruthy())
    vm.$refs.submissionForm.multiple = true
    const form = vm.$getForm('newUpload')
    form.step = 2
    await vm.$nextTick()
    await wrapper.findComponent('.submit-button').trigger('click')
    expect(mockAxios.request).toHaveBeenCalled()
    const submission = genSubmission()
    mockAxios.mockResponse(rs(submission))
    await flushPromises()
    await vm.$nextTick()
    expect(mockPush).not.toHaveBeenCalled()
    expect(form.step).toBe(1)
  })
  test('Shows the upload form based on vuex state', async() => {
    // v-dialog__content--active
    const user = genUser()
    user.id = 1
    setViewer(store, user)
    const mockPush = vi.fn()
    wrapper = mount(DummySubmit, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Fox'},
            query: {editing: false},
          },
          $router: {push: mockPush},
        },
      }),
      props: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.findComponent('#form-newUpload').isVisible()).toBe(true)
    expect(store.state.uploadVisible).toBe(true)
    await wrapper.findComponent('.dialog-closer').trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.uploadVisible).toBe(false)
    await wrapper.vm.$nextTick()
    expect(wrapper.findComponent('#form-newUpload').isVisible()).toBe(false)
  })
})
