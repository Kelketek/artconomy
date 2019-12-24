import Vue from 'vue'
import {Vuetify} from 'vuetify'
import {mount, Wrapper} from '@vue/test-utils'
import {cleanUp, createVuetify, flushPromises, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import DummySubmit from '@/components/specs/DummySubmit.vue'
import mockAxios from '@/__mocks__/axios'
import {genSubmission} from '@/store/submissions/specs/fixtures'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('AcNewSubmission.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
    store = createStore()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts the submission form', async() => {
    setViewer(store, genUser())
    wrapper = mount(DummySubmit, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox'},
      mocks: {$route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}}},
      sync: false,
      attachToDocument: true,
    })
  })
  it('Toggles the isArtist computed field', async() => {
    const user = genUser()
    user.id = 1
    setViewer(store, user)
    wrapper = mount(DummySubmit, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox'},
      mocks: {$route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}}},
      sync: false,
      attachToDocument: true,
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
  it('Submits and pushes you to the new Submission', async() => {
    const user = genUser()
    user.id = 1
    setViewer(store, user)
    const mockPush = jest.fn()
    wrapper = mount(DummySubmit, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox'},
      mocks: {
        $route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}},
        $router: {push: mockPush},
      },
      sync: false,
      attachToDocument: true,
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    mockAxios.reset()
    const form = vm.$getForm('newUpload')
    form.step = 2
    await vm.$nextTick()
    wrapper.find('.submit-button').trigger('click')
    expect(mockAxios.post).toHaveBeenCalled()
    const submission = genSubmission()
    submission.id = 3
    mockAxios.mockResponse(rs(submission))
    await flushPromises()
    await vm.$nextTick()
    expect(mockPush).toHaveBeenCalledWith({
      name: 'Submission', params: {submissionId: '3'}, query: {editing: 'true'},
    })
  })
  it('Shows the upload form based on vuex state', async() => {
    // v-dialog__content--active
    const user = genUser()
    user.id = 1
    setViewer(store, user)
    const mockPush = jest.fn()
    wrapper = mount(DummySubmit, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox'},
      mocks: {
        $route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}},
        $router: {push: mockPush},
      },
      sync: false,
      attachToDocument: true,
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-dialog__content--active').exists()).toBe(true)
    expect(store.state.uploadVisible).toBe(true)
    wrapper.find('.dialog-closer').trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.uploadVisible).toBe(false)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-dialog__content--active').exists()).toBe(false)
  })
})
