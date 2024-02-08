import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import AcVideoPlayer from '@/components/AcVideoPlayer.vue'
import {afterEach, beforeEach, describe, test, vi} from 'vitest'

let wrapper: VueWrapper<any>

const mockError = vi.spyOn(console, 'error')

describe('AcVideoPlayer.vue', () => {
  beforeEach(() => {
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Loads up for a video file', async() => {
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.mp3'}
    wrapper = mount(AcVideoPlayer, {
      ...vueSetup(),
      props: {asset: submission},
    })
  })
})
