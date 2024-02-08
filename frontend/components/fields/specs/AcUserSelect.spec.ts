import {VueWrapper} from '@vue/test-utils'
import {cleanUp, docTarget, flushPromises, mount, rq, rs, vueSetup} from '@/specs/helpers/index.ts'
import AcUserSelect from '@/components/fields/AcUserSelect.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {describe, expect, afterEach, test, vi} from 'vitest'

vi.useFakeTimers()
let wrapper: VueWrapper<any>

describe('AcUserSelect.vue', () => {
  afterEach(() => {
    vi.clearAllTimers()
    cleanUp(wrapper)
  })
  test('Searches for users', async() => {
    const tagList: number[] = []
    wrapper = mount(AcUserSelect, {
      ...vueSetup(),
      props: {modelValue: tagList},
    })
    wrapper.vm.query = 'Test'
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    expect(mockAxios.request).toHaveBeenCalled()
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/search/user/',
      'get',
      undefined,
      {
        signal: expect.any(Object),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        params: {q: 'Test'},
      },
    ))
  })
  test('Searches for users with a tagging modifier', async() => {
    const tagList: number[] = []
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {
          modelValue: tagList,
          tagging: true,
        },
      },
    )
    wrapper.vm.query = 'Test'
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    expect(mockAxios.request).toHaveBeenCalled()
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/search/user/',
      'get',
      undefined,
      {
        signal: expect.any(Object),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        params: {
          q: 'Test',
          tagging: true,
        },
      },
    ))
  })
  test('Accepts a response from the server on its query', async() => {
    const tagList: number[] = []
    wrapper = mount(AcUserSelect, {
      ...vueSetup(),
      props: {modelValue: tagList},
    })
    wrapper.vm.query = 'Test'
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    mockAxios.mockResponse(rs({
      results: [{
        username: 'Test',
        id: 1,
      }, {
        username: 'Test2',
        id: 2,
      }],
    }))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).items).toEqual([{
      username: 'Test',
      id: 1,
    }, {
      username: 'Test2',
      id: 2,
    }])
  })
  test('Sets a tag and resets upon adding a space when mode is multiple.', async() => {
    const tagList: number[] = []
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {modelValue: tagList},
      },
    )
    wrapper.vm.query = 'Test'
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    mockAxios.mockResponse(rs({
      results: [{
        username: 'Test',
        id: 1,
      }, {
        username: 'Test2',
        id: 2,
      }],
    }))
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.vm.query = 'Test '
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    expect((wrapper.vm as any).tags).toEqual([1])
    expect((wrapper.vm as any).query).toBe('')
  })
  test('Sets a tag and resets upon adding a space when mode is not multiple.', async() => {
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {
          modelValue: null,
          multiple: false,
        },
      },
    )
    wrapper.vm.query = 'Test'
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    mockAxios.mockResponse(rs({
      results: [{
        username: 'Test',
        id: 1,
      }, {
        username: 'Test2',
        id: 2,
      }],
    }))
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.vm.query = 'Test '
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual(1)
    expect((wrapper.vm as any).query).toBe('')
  })
  test('Does nothing to the query if adding a space with no results.', async() => {
    const tagList: number[] = []
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {modelValue: tagList},
      },
    )
    wrapper.vm.query = 'Test'
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    mockAxios.mockResponse(rs({results: []}))
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.vm.query = 'Test '
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual([])
    expect((wrapper.vm as any).query).toBe('Test ')
  })
  test('Prepopulates with initial items', async() => {
    const tagList: number[] = []
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        attachTo: docTarget(),
        props: {
          modelValue: tagList,
          initItems: [{
            username: 'Test',
            id: 1,
          }, {
            username: 'Test2',
            id: 2,
          }],
        },
      },
    )
    expect((wrapper.vm as any).items).toEqual([{
      username: 'Test',
      id: 1,
    }, {
      username: 'Test2',
      id: 2,
    }])
  })
  test('Resets the query if adding an item', async() => {
    const tagList: number[] = [1]
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {
          modelValue: tagList,
          initItems: [{
            username: 'Test',
            id: 1,
          }, {
            username: 'Test2',
            id: 2,
          }],
        },
      },
    )
    wrapper.vm.query = 'Test'
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    await wrapper.setProps({modelValue: [1, 2]})
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).query).toBe('')
  })
  test('Does not reset the query if removing an item', async() => {
    const tagList: number[] = [1, 2]
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {
          modelValue: tagList,
          initItems: [{
            username: 'Test',
            id: 1,
          }, {
            username: 'Test2',
            id: 2,
          }],
        },
      },
    )
    wrapper.vm.query = 'Test'
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    await wrapper.setProps({modelValue: [1]})
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).query).toBe('Test')
  })
  test('Always returns false when filtering an empty string', async() => {
    const tagList: number[] = [1]
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {
          modelValue: tagList,
          initItems: [{
            username: 'Test',
            id: 1,
          }, {
            username: 'Test2',
            id: 2,
          }],
        },
      },
    )
    const vm = wrapper.vm as any
    const user = genUser()
    expect(vm.itemFilter(user, '', 'Fox')).toBe(false)
  })
  test('Returns false when already selected for the single item', async() => {
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {
          modelValue: null,
          multiple: false,
          initItems: [{
            username: 'Test',
            id: 1,
          }, {
            username: 'Test2',
            id: 2,
          }],
        },
      },
    )
    const vm = wrapper.vm as any
    const user = {
      username: 'Test',
      id: 1,
    }
    expect(vm.itemFilter(user, 'Test', 'Test')).toBe(true)
    await wrapper.setProps({
      modelValue: 1,
      multiple: false,
      initItems: [{
        username: 'Test',
        id: 1,
      }, {
        username: 'Test2',
        id: 2,
      }],
    })
    await wrapper.vm.$nextTick()
    expect(vm.itemFilter(user, 'Test', 'Test')).toBe(false)
  })
  test('Calls a custom filter', () => {
    const mockFilter = vi.fn()
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {
          modelValue: 1,
          multiple: false,
          initItems: [{
            username: 'Test',
            id: 1,
          }, {
            username: 'Test2',
            id: 2,
          }],
          filter: mockFilter,
        },
      },
    )
    const vm = wrapper.vm as any
    const user = {
      username: 'Test',
      id: 1,
    }
    vm.itemFilter(user, 'Test', 'Test')
    expect(mockFilter).toHaveBeenCalledWith(user, 'Test', 'Test')
  })
  test('Clears tags when upstream clears them', async() => {
    wrapper = mount(
      AcUserSelect, {
        ...vueSetup(),
        props: {
          modelValue: [1],
          initItems: [{
            username: 'Test',
            id: 1,
          }, {
            username: 'Test2',
            id: 2,
          }],
        },
      },
    )
    const vm = wrapper.vm as any
    expect(vm.tags).toEqual([1])
    await wrapper.setProps({
      modelValue: null,
      initItems: [{
        username: 'Test',
        id: 1,
      }, {
        username: 'Test2',
        id: 2,
      }],
    })
    await vm.$nextTick()
    expect(vm.tags).toEqual([])
  })
})
