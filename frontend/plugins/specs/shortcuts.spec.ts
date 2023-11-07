import ViewerComponent from '@/specs/helpers/dummy_components/viewer.vue'
import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import {genUser} from '@/specs/helpers/fixtures'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

let store: ArtStore
let vm: any
const fox = genUser()
fox.rating = 2

describe('shortcuts.ts', () => {
  beforeEach(() => {
    store = createStore()
    setViewer(store, fox)
    vm = mount(ViewerComponent, vueSetup({store})).vm
  })
  afterEach(() => {
    cleanUp()
  })
  test('Handles a null asset', async() => {
    expect(vm.$img(null, 'preview', true)).toBe('/static/images/default-avatar.png')
  })
  test('Handles a submission with a viewable rating', async() => {
    const submission = genSubmission()
    submission.rating = 2
    expect(vm.$img(submission, 'thumbnail', true)).toBe(
      'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png',
    )
    expect(vm.$img(submission, 'blabla', false)).toBe(undefined)
  })
  test('Handles a submission with an unviewable rating', async() => {
    const adultSubmission = genSubmission()
    adultSubmission.rating = 3
    expect(vm.$img(adultSubmission, 'thumbnail', true)).toBe(
      '/static/images/default-avatar.png',
    )
    expect(vm.$img(adultSubmission, 'thumbnail', false)).toBe(
      '',
    )
  })
  test('Handles a submission with a preview', async() => {
    const submission = genSubmission()
    submission.preview = {
      thumbnail: '/test/image.png',
    }
    expect(vm.$img(submission, 'thumbnail', true)).toBe(
      '/test/image.png',
    )
    expect(vm.$img(submission, 'gallery', false)).toBe(
      'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png',
    )
  })
  test('Handles an SVG', async() => {
    const submission = genSubmission()
    submission.file.full = '/test/image.svg'
    expect(vm.$img(submission, 'thumbnail', true)).toBe(
      '/test/image.svg',
    )
  })
  test('Handles a non-image file thumbnail', async() => {
    const submission = genSubmission()
    submission.file.full = '/test/image.mp4'
    expect(vm.$img(submission, 'thumbnail', true)).toBe(
      '/static/icons/MP4.png',
    )
  })
})
