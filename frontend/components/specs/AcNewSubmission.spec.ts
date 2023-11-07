import {VueWrapper} from '@vue/test-utils'
import {cleanUp, flushPromises, mount, rs, setViewer, vueSetup, VuetifyWrapped} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import DummySubmit from '@/components/specs/DummySubmit.vue'
import mockAxios from '@/__mocks__/axios'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

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
    const mockPush = vi.fn()
    wrapper = mount(WrappedDummySubmit, {
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
    const vm = wrapper.vm as any
    await vm.$nextTick()
    mockAxios.reset()
    const form = vm.$getForm('newUpload')
    form.step = 2
    await vm.$nextTick()
    await wrapper.find('.submit-button').trigger('click')
    expect(mockAxios.request).toHaveBeenCalled()
    const submission = genSubmission()
    submission.id = 3
    mockAxios.mockResponse(rs(submission))
    await flushPromises()
    await vm.$nextTick()
    expect(mockPush).toHaveBeenCalledWith({
      name: 'Submission',
      params: {submissionId: '3'},
      query: {editing: 'true'},
    })
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
            query: {editing: false},
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
    await vm.$nextTick()
    mockAxios.reset()
    vm.$refs.submissionForm.multiple = true
    const form = vm.$getForm('newUpload')
    form.step = 2
    await vm.$nextTick()
    await wrapper.find('.submit-button').trigger('click')
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
    expect(wrapper.find('.v-overlay--active').exists()).toBe(true)
    expect(store.state.uploadVisible).toBe(true)
    await wrapper.find('.dialog-closer').trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.uploadVisible).toBe(false)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-overlay--active').exists()).toBe(false)
  })
})
