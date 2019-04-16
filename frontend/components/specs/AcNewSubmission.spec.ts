import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {flushPromises, rs, setViewer, vuetifySetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import {characterRegistry, Characters} from '@/store/characters/registry'
import {listRegistry, Lists} from '@/store/lists/registry'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import DummySubmit from '@/components/specs/DummySubmit.vue'
import mockAxios from '@/__mocks__/axios'
import {genSubmission} from '@/store/submissions/specs/fixtures'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Profiles)
localVue.use(Lists)
localVue.use(Characters)
localVue.use(FormControllers)
let wrapper: Wrapper<Vue>
let store: ArtStore

const mockError = jest.spyOn(console, 'error')

describe('AcTagDisplay.vue', () => {
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    profileRegistry.reset()
    characterRegistry.reset()
    listRegistry.reset()
    formRegistry.reset()
    mockError.mockClear()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts the submission form', async() => {
    setViewer(store, genUser())
    wrapper = mount(DummySubmit, {
      localVue,
      store,
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
    form.step = 3
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
      propsData: {username: 'Fox'},
      mocks: {
        $route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}},
        $router: {push: mockPush},
      },
      sync: false,
      attachToDocument: true,
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-dialog__content--active').exists()).toBe(false)
    expect(store.state.uploadVisible).toBe(false)
    store.commit('setUploadVisible', true)
    expect(store.state.uploadVisible).toBe(true)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-dialog__content--active').exists()).toBe(true)
    wrapper.find('.dialog-closer').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-dialog__content--active').exists()).toBe(false)
    expect(store.state.uploadVisible).toBe(false)
  })
})
