import {VueWrapper} from '@vue/test-utils'
import {cleanUp, flushPromises, mount, rq, rs, vueSetup} from '@/specs/helpers/index.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import AcMarkdownViewer from '@/components/AcMarkdownViewer.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let wrapper: VueWrapper<any>

const mockError = vi.spyOn(console, 'error')

describe('AcMarkdownViewer.vue', () => {
  beforeEach(() => {
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Loads and renders a markdown document', async() => {
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/test.txt'}
    // @ts-ignore
    wrapper = mount(AcMarkdownViewer, {
      ...vueSetup(),
      props: {asset: submission},
    })
    expect(mockAxios.request).toHaveBeenCalledWith(rq('https://example.com/test.txt', 'get', undefined, {}))
    mockAxios.mockResponse(rs('# Hello!'))
    await flushPromises()
    expect(wrapper.find('h1').text()).toEqual('Hello!')
  })
})
