import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import DummyShare from '@/components/specs/DummyShare.vue'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore

const mockError = vi.spyOn(console, 'error')

describe('AcShareButton.vue', () => {
  beforeEach(() => {
    store = createStore()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts a share button and resolves a URL', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    const single = mount(Empty, vueSetup({store})).vm.$getSingle('submission', {endpoint: '/'})
    const mockResolve = vi.fn()
    single.setX(submission)
    mockResolve.mockImplementation(() => ({href: '/stuff/'}))
    wrapper = mount(DummyShare, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Fox'},
            query: {editing: false},
          },
          $router: {resolve: mockResolve},
        },
      }),
      props: {title: 'Sharable thing!'},
    })
    expect(mockResolve).toHaveBeenCalledWith({
      name: 'Profile',
      params: {username: 'Fox'},
      query: {
        editing: false,
        referred_by: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    expect(vm.$refs.shareButton.referral).toBe(true)
    await wrapper.find('.share-button').trigger('click')
    await vm.$nextTick()
    await wrapper.find('.referral-check input').trigger('click')
    await wrapper.vm.$nextTick()
    expect(vm.$refs.shareButton.referral).toBe(false)
    expect(mockResolve).toHaveBeenCalledWith({
      name: 'Profile',
      params: {username: 'Fox'},
      query: {editing: false},
    })
  })
  test('Closes out of the whole menu when the QR menu is closed', async() => {
    setViewer(store, genUser())
    const submission = genSubmission()
    const single = mount(Empty, vueSetup({store})).vm.$getSingle('submission', {endpoint: '/'})
    const mockResolve = vi.fn()
    single.setX(submission)
    mockResolve.mockImplementation(() => ({href: '/stuff/'}))
    wrapper = mount(DummyShare, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Profile',
            params: {username: 'Fox'},
            query: {editing: false},
          },
          $router: {resolve: mockResolve},
        },
      }),
      props: {title: 'Sharable thing!'},
    })
    const vm = wrapper.vm as any
    const share = vm.$refs.shareButton
    await vm.$nextTick()
    await wrapper.find('.share-button').trigger('click')
    await vm.$nextTick()
    expect(share.showModal).toBe(true)
    expect(share.showQr).toBe(false)
    await wrapper.find('.qr-button').trigger('click')
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
