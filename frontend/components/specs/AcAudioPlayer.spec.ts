import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import AcAudioPlayer from '@/components/AcAudioPlayer.vue'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let wrapper: VueWrapper<any>

const mockError = vi.spyOn(console, 'error')

describe('AcAudioPlayer.vue', () => {
  beforeEach(() => {
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Loads and types an audio file', async() => {
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.mp3'}
    wrapper = mount(AcAudioPlayer, {
      ...vueSetup(),
      props: {asset: submission, alt: 'Beep'},
    })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('audio/mp3')
  })
})
