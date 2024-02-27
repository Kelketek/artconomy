import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, vueSetup, waitFor} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import AcAsset from '@/components/AcAsset.vue'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {nextTick} from 'vue'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>

const mockError = vi.spyOn(console, 'error')

describe('AcAsset.vue', () => {
  beforeEach(() => {
    store = createStore()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Loads and previews an asset', async() => {
    setViewer(store, genUser())
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: genSubmission(),
        thumbName: 'full',
        alt: '',
      },
    })
    await nextTick()
    expect(wrapper.find('.asset-image').find('img').attributes()['src']).toBe('https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png')
  })
  test('Does not load an asset if the viewer is nerfed.', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.sfw_mode = true
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: submission,
        thumbName: 'full',
        alt: '',
      },
    })
    await nextTick()
    const vm = wrapper.vm as any
    expect(wrapper.find('.asset-image').exists()).toBe(false)
    expect(vm.nerfed).toBe(true)
    expect(wrapper.find('.nerfed-message').exists()).toBe(true)
  })
  test('Does not load an asset if the maximum rating is under the asset rating.', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.rating = 1
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: submission,
        thumbName: 'full',
        alt: '',
      },
    })
    await nextTick()
    const vm = wrapper.vm as any
    expect(wrapper.find('.asset-image').exists()).toBe(false)
    expect(vm.nerfed).toBe(false)
    expect(wrapper.find('.rating-info').exists()).toBe(true)
  })
  test('Uses a sensible default aspect ratio if the image cannot be displayed and none is specified.',
    async() => {
      const viewer = genUser()
      const submission = genSubmission()
      submission.rating = 2
      viewer.rating = 1
      setViewer(store, viewer)
      wrapper = mount(AcAsset, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {
          asset: submission,
          thumbName: 'full',
          aspectRatio: null,
          alt: '',
        },
      })
      await nextTick()
      const vm = wrapper.vm as any
      expect(vm.ratio).toBe(1)
    })
  test('Handles a null asset', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.rating = 1
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: null,
        thumbName: 'full',
        alt: '',
      },
    })
    await nextTick()
    const vm = wrapper.vm as any
    expect(wrapper.find('.asset-image').find('img').attributes()['src']).toBe('/static/images/default-avatar.png')
    // Since the output will be an image, we consider this true.
    expect(vm.isImage).toBe(true)
    expect(vm.blacklisted).toEqual([])
    expect(vm.displayComponent).toBe(null)
  })
  test('Handles a null asset with a custom fallback URL', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.rating = 1
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: null,
        thumbName: 'full',
        fallbackImage: 'boop.jpg',
        alt: '',
      },
    })
    await nextTick()
    expect(wrapper.find('.asset-image').find('img').attributes()['src']).toBe('boop.jpg')
  })
  test('Handles an anonymous user', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.rating = 1
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: null,
        thumbName: 'full',
        alt: '',
      },
    })
    await nextTick()
    const vm = wrapper.vm as any
    expect(wrapper.find('.asset-image').find('img').attributes()['src']).toBe('/static/images/default-avatar.png')
    expect(vm.isImage).toBe(true)
    expect(vm.blacklisted).toEqual([])
  })
  test('Handles alternative file types', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.file = {
      full: 'https://example.com/thing.mp4',
      __type__: 'data:swf',
    }
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: submission,
        thumbName: 'full',
        alt: '',
      },
    })
    await nextTick()
    expect(wrapper.find('.asset-image').exists()).toBe(false)
    await waitFor(() => expect(wrapper.find('.ac-video-player').exists()).toBe(true))
  })
  test('Displays a thumbnail', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: submission,
        thumbName: 'thumbnail',
        alt: '',
      },
    })
    await nextTick()
    expect(wrapper.find('.asset-image').find('img').attributes()['src']).toBe(
      'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png',
    )
  })
  test('Displays a preview', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.preview = {thumbnail: 'https://example.com/thing.jpg'}
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: submission,
        thumbName: 'thumbnail',
        alt: '',
      },
    })
    await nextTick()
    expect(wrapper.find('.asset-image').find('img').attributes()['src']).toBe(
      'https://example.com/thing.jpg',
    )
  })
  test('Handles a non-previewable file type', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.file = {
      full: 'https://example.com/thing.doc',
      __type__: 'data:word',
    }
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: submission,
        thumbName: 'thumbnail',
        alt: '',
      },
    })
    await nextTick()
    expect(wrapper.find('.icon-image').find('img').attributes()['src']).toBe(
      '/static/icons/DOC.png',
    )
  })
  test('Handles the special case of an SVG', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.file = {
      full: 'https://example.com/thing.svg',
      __type__: 'data:image',
    }
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: submission,
        thumbName: 'thumbnail',
        alt: '',
      },
    })
    await nextTick()
    expect(wrapper.find('.asset-image').find('img').attributes()['src']).toBe(
      'https://example.com/thing.svg',
    )
  })
  test('Handles the special case of a GIF', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.file = {
      full: 'https://example.com/thing.gif',
      gallery: 'https://example.com/thumb.gif',
      __type__: 'data:image',
    }
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: submission,
        thumbName: 'gallery',
        alt: '',
      },
    })
    await nextTick()
    expect(wrapper.find('.asset-image').find('img').attributes()['src']).toBe(
      'https://example.com/thing.gif',
    )
  })
  test('Hides the asset if item has a blacklisted tag', async() => {
    const viewer = genUser()
    viewer.blacklist.push('fuckable', 'bork')
    const submission = genSubmission()
    submission.file = {
      full: 'https://example.com/thing.svg',
      __type__: 'data:svg',
    }
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {
        asset: submission,
        thumbName: 'thumbnail',
        alt: '',
      },
    })
    await nextTick()
    const vm = wrapper.vm as any
    await nextTick()
    expect(vm.blacklisted).toEqual(['fuckable'])
    expect(vm.canDisplay).toBe(false)
    expect(wrapper.find('.blacklist-info').exists()).toBe(true)
    expect(wrapper.find('.asset-image').exists()).toBe(false)
  })
})
