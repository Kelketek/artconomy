import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {singleRegistry} from '@/store/singles/registry'
import {profileRegistry} from '@/store/profiles/registry'
import {setViewer, vueSetup, vuetifySetup} from '@/specs/helpers'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import DummyShare from '@/components/specs/DummyShare.vue'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore

const mockError = jest.spyOn(console, 'error')

describe('AcTagDisplay.vue', () => {
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    profileRegistry.reset()
    mockError.mockClear()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts a share button and resolves a URL', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    const single = mount(Empty, {localVue, store, attachToDocument: true, sync: false}).vm.$getSingle('submission', {endpoint: '/'})
    const mockResolve = jest.fn()
    single.setX(submission)
    mockResolve.mockImplementation(() => ({href: '/stuff/'}))
    wrapper = mount(DummyShare, {
      localVue,
      store,
      propsData: {title: 'Sharable thing!'},
      mocks: {
        $route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}},
        $router: {resolve: mockResolve},
      },
      sync: false,
      attachToDocument: false,
    })
    expect(mockResolve).toHaveBeenCalledWith({
      name: 'Profile', params: {username: 'Fox'}, query: {editing: false, referred_by: 'Fox'},
    })
    const vm = wrapper.vm as any
    expect(vm.$refs.shareButton.referral).toBe(true)
    wrapper.find('.referral-check input').trigger('click')
    await wrapper.vm.$nextTick()
    expect(vm.$refs.shareButton.referral).toBe(false)
    expect(mockResolve).toHaveBeenCalledWith({
      name: 'Profile', params: {username: 'Fox'}, query: {editing: false},
    })
  })
  it('Closes out of the whole menu when the QR menu is closed', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    const single = mount(Empty, {localVue, store, attachToDocument: true, sync: false}).vm.$getSingle('submission', {endpoint: '/'})
    const mockResolve = jest.fn()
    single.setX(submission)
    mockResolve.mockImplementation(() => ({href: '/stuff/'}))
    wrapper = mount(DummyShare, {
      localVue,
      store,
      propsData: {title: 'Sharable thing!'},
      mocks: {
        $route: {name: 'Profile', params: {username: 'Fox'}, query: {editing: false}},
        $router: {resolve: mockResolve},
      },
      sync: false,
      attachToDocument: false,
    })
    const vm = wrapper.vm as any
    const share = vm.$refs.shareButton
    await vm.$nextTick()
    wrapper.find('.share-button').trigger('click')
    await vm.$nextTick()
    expect(share.showModal).toBe(true)
    expect(share.showQr).toBe(false)
    wrapper.find('.qr-button').trigger('click')
    await vm.$nextTick()
    expect(share.showModal).toBe(true)
    expect(share.showQr).toBe(true)
    // Can't query proper dialog with certainty because the class cannot be annotated. We'll just verify the watcher
    // works at this point.
    share.showQr = false
    await vm.$nextTick()
    expect(share.showQr).toBe(false)
    expect(share.showModal).toBe(false)
  })
})
