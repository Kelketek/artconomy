import {VueWrapper} from '@vue/test-utils'
import {cleanUp, createTestRouter, mount, vueSetup, waitFor} from '@/specs/helpers/index.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import DummyShare from '@/components/specs/DummyShare.vue'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import {nextTick} from 'vue'

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
    setViewer({ store, user: genUser() })
    const submission = genSubmission()
    const router = createTestRouter()
    const single = mount(Empty, vueSetup({store})).vm.$getSingle('submission', {endpoint: '/'})
    single.setX(submission)
    await router.push({
      name: 'Profile',
      params: {username: 'Fox'},
      query: {editing: 'false'},
    })
    wrapper = mount(DummyShare, {
      ...vueSetup({
        store,
        router,
      }),
      props: {title: 'Sharable thing!'},
    })
    // expect(mockResolve).toHaveBeenCalledWith({
    //   name: 'Profile',
    //   params: {username: 'Fox'},
    //   query: {
    //     editing: false,
    //     referred_by: 'Fox',
    //   },
    // })
    await waitFor(() => expect(wrapper.vm.$refs.shareButton).toBeTruthy())
    const vm = wrapper.vm.$refs.shareButton
    expect(vm.referral).toBe(true)
    expect(vm.baseRawLocation).toBe('http://localhost:3000/profile/Fox/?editing=false&referred_by=Fox')
    await wrapper.find('.share-button').trigger('click')
    await vm.$nextTick()
    await wrapper.findComponent('.referral-check').find('input').trigger('click')
    await nextTick()
    expect(vm.referral).toBe(false)
  })
  test('Closes out of the whole menu when the QR menu is closed', async() => {
    setViewer({ store, user: genUser() })
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
    await wrapper.findComponent('.qr-button').trigger('click')
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
