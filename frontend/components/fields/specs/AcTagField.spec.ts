import {VueWrapper} from '@vue/test-utils'
import {cleanUp, flushPromises, mount, rq, rs, vueSetup} from '@/specs/helpers'
import AcTagField from '@/components/fields/AcTagField.vue'
import mockAxios from '@/__mocks__/axios'
import {describe, expect, afterEach, test, vi, beforeEach} from 'vitest'

let wrapper: VueWrapper<any>

describe('ac-tag-field', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Searches for tags', async() => {
    const tagList: string[] = []
    wrapper = mount(AcTagField, {
      ...vueSetup(),
      props: {modelValue: tagList},
    })
    wrapper.vm.query = 'Test'
    vi.runAllTimers()
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/search/tag/',
      'get',
      undefined,
      {
        signal: expect.any(Object),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        params: {q: 'Test'},
      },
    ))
  })
  test('Accepts a response from the server on its query', async() => {
    const tagList: string[] = []
    wrapper = mount(AcTagField, {
      ...vueSetup(),
      props: {modelValue: tagList},
    })
    wrapper.vm.query = 'Test'
    vi.runAllTimers()
    mockAxios.mockResponse(rs(['Test', 'Test1', 'Test2']))
    await flushPromises()
  })
  test('Sets a tag and resets upon adding a space.', async() => {
    const tagList: string[] = []
    wrapper = mount(
      AcTagField, {
        ...vueSetup(),
        props: {modelValue: tagList},
      })
    wrapper.vm.query = 'Test '
    vi.runAllTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual(['Test'])
    expect((wrapper.vm as any).queryStore).toBe('')
  })
  test('Does not redundantly add a tag.', async() => {
    const tagList: string[] = ['Test']
    wrapper = mount(
      AcTagField, {
        ...vueSetup(),
        props: {modelValue: tagList},
      })
    wrapper.vm.query = 'Test '
    vi.runAllTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual(['Test'])
    expect((wrapper.vm as any).queryStore).toBe('')
  })
})
